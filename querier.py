from abc import ABC, abstractmethod
from typing import List
import openai
import os
import sys
import subprocess
import re
import json
import difflib
import file_utilities
import uuid
import pprint
from termcolor import colored

class FunctionCall():
	def __init__(self, type, function_identifier, call_identifier, context):
		self.type = type
		self.function_identifier = function_identifier
		self.call_identifier = call_identifier
		self.context = context

	def __str__(self):
		return f"FunctionCall(type={self.type}, function_identifier={self.function_identifier}, call_identifier={self.call_identifier}, context={self.context})"

class AIModelQuerier(ABC):
	"""
	Abstract base class for AI models.
	"""
	
	def __init__(self, model_identifier: str):
		self._model_identifier = model_identifier
	
	@property
	def model_identifier(self) -> str:
		"""
		A unique identifier for the model.
		"""
		return self._model_identifier
	
	@classmethod
	def supported_model_names(cls):
		return []
		
	@abstractmethod
	def get_output(self, input):
		pass
	
	@classmethod
	def resolve_queriers(cls, model_names: List[str], force_human: bool = False):
		subclass_mapping = {model_name: subclass for subclass in cls.__subclasses__() 
							for model_name in subclass.supported_model_names()}	
		if force_human:
			subclass_mapping = {}
		instances = []
		for model_name in model_names:
			subclass = subclass_mapping.get(model_name)
			instances.append(subclass(model_name))
		return instances
	
	@classmethod
	def initial_prompt(cls):
		return "Act as a human who is using the lldb debugger to identify and fix crashes in a running process. You will be provided with output from lldb, and are able to issue commands to lldb to identify the issue. You can also apply patches."#Issue only one command per message. Enclose that command in a Markdown code block. Do not include the (lldb) command-line prompt or anything else in the Markdown code block.\n\nOnce you have identified the problem, provide a patch that can be applied using the diff tool to fix the issue. Enclose the diff in a Markdown code block marked with 'diff'. Format the diff so that it can be applied directly via `patch -p0` applied in the same directory as the file paths are relative to."
		
		#\n\nThe debugger is already running and has stopped at the beginning of the program so that you can inspect the program and set breakpoints as necessary.\n\n
		
	@classmethod
	def transient_prompt(cls):
		return "Analyze the output of any previous function calls and decide what to do next. Before issuing the next command you must explain your reasoning about what command to issue and why it will help with the debugging of the process. When issuing debugger command, be sure that the correct frame is selected using 'frame select' before issuing frame-specific commands like 'frame variable'. Where possible, use the 'get_source' function instead of using the 'list' debugger command."
		
	def handle_debugger_output(cls, output):
		return self.get_output(output)

	def __str__(self) -> str:
		return f"{self.__class__.__name__}(model_identifier={self.model_identifier})"

class OpenAIModelQuerier(AIModelQuerier):
	@classmethod
	def supported_model_names(cls):
		# Make sure this key is set before trying to interact with the OpenAI API
		if 'OPENAI_API_KEY' in os.environ:
			response = openai.Model.list()
			return [item['id'] for item in response['data']]
		else:
			print("Warning: No OpenAI API key found in environment. Set the OPENAI_API_KEY environment variable.")
			return []
			
	def __init__(self, model_identifier: str):
		super().__init__(model_identifier)
		initial_prompt = AIModelQuerier.initial_prompt()
		print(f"***Initial prompt: {colored(initial_prompt, 'cyan')}")
		self.messages = [{"role": "system", "content": initial_prompt}]
		self._pending_context = []
		self._output_context_identifier = uuid.uuid4()

		
	def load_context(self, context_identifier):
		self._pending_context = file_utilities.retrieve_context(context_identifier)
		
	def save_context(self, context_identifier):
		file_utilities.store_context(self.messages, context_identifier)
		
	def get_context_identifier(self):
		return self._output_context_identifier
			
	def is_chat_based_model(self):
		return "gpt-3.5" in self.model_identifier or "gpt-4" in self.model_identifier
	
	def extract_code_and_type(self, response: str) -> tuple:
		# Try to find the last code block with any keyword after the ticks or without any keyword
		blocks = re.findall(r'``` *\s*(\w*)\n(.*?)\n```', response, re.DOTALL)
		if blocks:
			code_type, code_content = blocks[-1]
			# Removing any (lldb) prompt from the extracted command
			code_content = re.sub(r'^(?:\(lldb\)\s*)?', '', code_content.strip())
			return (code_type, code_content)
		
		# If no code blocks are found, look for lines starting with an optional (lldb) prompt followed by a command
		command_lines = re.findall(r'^(?:\(lldb\)\s*)?(.*)$', response, re.MULTILINE)
		if command_lines:
			return ('', command_lines[-1].strip())  # Return the last command line found with no type
		
		return ('', response)

	def get_tools(self):
		return [
			{
				"type": "function",
				"function":  {
					"name": "run_debugger_command",
					"description": "Run a command using the lldb debugger.",
					"parameters": {
						"type": "object",
						"properties": {
							"cmd": {
								"type": "string",
								"description": "The command to run.",
							},
						},
						"required": ["cmd"],
					},
				}
			},
			{
				"type": "function",
				"function":  {
					"name": "get_source",
					"description": "Retrieve the contents of a particular source file, centered around a given line number.",
					"parameters": {
						"type": "object",
						"properties": {
							"file_path": {
								"type": "string",
								"description": "The path of the source file to read.",
							},
							"line_number": {
								"type": "integer",
								"description": "The line number of interest.",
							},
							"context_lines": {
								"type": "integer",
								"description": "The number of lines before and after the line of interest to display. Defaults to 10.",
							},
						},
						"required": ["file_path", "line_number"],
					},
				}
			},
			{
				"type": "function",
				"function": {
					"name": "modify_code",
					"description": "Modify the source code, recompile, and restart the debugger to test changes.",
					"parameters": {
						"type": "object",
						"properties": {
							"file_path": {
								"type": "string",
								"description": "The path of the file to modify as shown in the debugger output.",
							},
							"changes": {
								"type": "array",
								"items": {
									"type": "object",
									"properties": {
										"from-file-range": {
											"type": "object",
											"properties": {
												"start-line": {
													"type": "integer",
													"description": "The first line in the original file that should be replaced. Line numbers start at 1.",
												},
												"code": {
													"type": "string",
													"description": "The code that should be replaced by the code in to-file-range.",
												}
											},
											"required": ["start-line", "code"]
										},
										"to-file-range": {
											"type": "object",
											"properties": {
												"start-line": {
													"type": "integer",
													"description": "The first line in the updated file that should be replaced. This should be the line number after previous changes in the array are applied. Line numbers start at 1.",
												},
												"code": {
													"type": "string",
													"description": "The code to replace the code in from-file-range.",
												}
											},
											"required": ["start-line", "code"]
										},
					
									}
								}
							}
						},
						"required": ["file_path", "changes"]
					},
				}
			},
			{
				"type": "function",
				"function": {
					"name": "restart",
					"description": "Restart debugging from the beginning.",
					"parameters": {
						"type": "object",
						"properties": {}
					}					
				}
			},
		]
		
	def validate_changes(self, source_code, change_dict):
		lines = source_code.splitlines()
		for change in change_dict["changes"]:
			start_line = change["from-file-range"]["start-line"] - 1
			num_lines = len(change["from-file-range"]["code"].splitlines())
			extracted_lines = [line.lstrip().rstrip() for line in lines[start_line:start_line + num_lines]]
			
			expected_lines = [line.lstrip().rstrip() for line in change["from-file-range"]["code"].splitlines()]
			
			# Direct line-by-line comparison
			if extracted_lines != expected_lines:
				error_message = "Mismatch starting at line {}. Expected: '{}' but found: '{}'".format(
					start_line + 1, "\n".join(expected_lines), "\n".join(extracted_lines))
				return False, error_message
		
		return True, "Changes are valid"

	def validate_changes_and_generate_unified_diff(self, data, base_path, context_lines=3):
		file_path = data["file_path"]
		source_code = file_utilities.get_source_code(base_path, file_path)
		if source_code is None:
			return False, f"Unable to get source code. Base path: {base_path}, file_path: {file_path}"
	
		# Step 1: Validate the changes
		is_valid, message = self.validate_changes(source_code, data)
		if not is_valid:
			return False, message
		
		# Split the source code into lines for easy access
		source_lines = source_code.splitlines()
		
	    # Initialize to_code as a full copy of source_lines
		to_code = source_lines.copy()
		
		# Apply each change to the to_code list
		for change in data["changes"]:
			start_line = change["from-file-range"]["start-line"] - 1
			end_line = start_line + len(change["from-file-range"]["code"].splitlines())
		
			change_lines = change["to-file-range"]["code"].splitlines()
			to_code[start_line:end_line] = change_lines

		# Generate unified diff using difflib with full source and modified code
		diff = difflib.unified_diff(
			source_lines, 
			to_code, 
			fromfile=file_path, 
			tofile=file_path, 
			lineterm='',
			n=context_lines
		)
		
		# Return the patch
		return True, "\n".join(diff)

	def strip_assistant_content(self, assistant_content):
		stripped_content = []
		
		for entry in assistant_content[:-1]:
			entry = entry.copy()
			# print(f"Entry: {entry}")
			if entry.get('role') == 'assistant' and 'content' in entry and len(entry) > 2:
				entry.pop('content')
			if 'role' in entry:
				stripped_content.append(entry)
		if len(assistant_content) > 1:
			stripped_content.append(assistant_content[-1])
		# print(f"Stripped content:")
		# pprint.pprint(stripped_content)
		return stripped_content

	def get_next_response_from_context(self):
		response = None
		while len(self._pending_context) > 0 and response is None:
			next_message = self._pending_context[0]
			if next_message['role'] == 'assistant':
				response = next_message
			self._pending_context.pop(0)
		return response
	
	def merge_chunks(self, chunks):
		# Function to recursively merge dictionaries
		def merge_dict(d1, d2):
			for key in d2:
				if key in d1:
					if isinstance(d1[key], dict) and isinstance(d2[key], dict):
						merge_dict(d1[key], d2[key])
					elif isinstance(d1[key], list) and isinstance(d2[key], list):
						d1[key] = merge_list(d1[key], d2[key])
					elif isinstance(d1[key], str) and isinstance(d2[key], str):
						d1[key] += d2[key]
					else:
						# If the types are mismatched or non-mergable, overwrite
						d1[key] = d2[key]
				else:
					d1[key] = d2[key]
	
		# Function to deeply merge lists, handling arbitrary depths of nested lists and dictionaries
		def merge_list(l1, l2):
			merged = []
			temp_dict = {}
	
			# Combine the lists for processing
			combined_list = l1 + l2
			for item in combined_list:
				if isinstance(item, dict) and 'index' in item:
					index = item['index']
					if index not in temp_dict:
						temp_dict[index] = item.copy()
					else:
						merge_dict(temp_dict[index], item)
				elif isinstance(item, list):
					# Find a matching list and merge
					list_match = next((elem for elem in merged if isinstance(elem, list)), None)
					if list_match:
						merged[merged.index(list_match)] = merge_list(list_match, item)
					else:
						merged.append(item)
				else:
					# For non-dictionary and non-list items, simply append if not already present
					if item not in merged:
						merged.append(item)
	
			# Append consolidated dictionaries from temp_dict to merged list
			for item in temp_dict.values():
				merged.append(item)
	
			return merged
	
		# Initialize an empty dictionary to store the merged content
		merged_object = {}
	
		# Iterate through the list of chunks
		for obj in chunks:
			obj_delta = obj['delta']  # Access the delta dict
	
			# Use the recursive merge function
			merge_dict(merged_object, obj_delta)
	
		return merged_object
	# 
	# def merge_chunks(self, chunks):
	# 	# Function to recursively merge dictionaries
	# 	def merge_dict(d1, d2):
	# 		for key in d2:
	# 			if key in d1:
	# 				if isinstance(d1[key], dict) and isinstance(d2[key], dict):
	# 					merge_dict(d1[key], d2[key])
	# 				elif isinstance(d1[key], list) and isinstance(d2[key], list):
	# 					d1[key].extend(d2[key])
	# 				elif isinstance(d1[key], str) and isinstance(d2[key], str):
	# 					d1[key] += d2[key]
	# 				else:
	# 					# If the types are mismatched or non-mergable, overwrite
	# 					d1[key] = d2[key]
	# 			else:
	# 				d1[key] = d2[key]
	# 	
	# 	# Initialize an empty dictionary to store the merged content
	# 	merged_object = {}
	# 	
	# 	# Iterate through the list of chunks
	# 	for obj in chunks:
	# 		obj_delta = obj['delta']  # Access the delta dict
	# 	
	# 		# Use the recursive merge function
	# 		merge_dict(merged_object, obj_delta)
	# 	
	# 	return merged_object

	def append_function_call_response(self, function_call, response):
		new_message = {"role": "tool", "name": function_call.function_identifier, "tool_call_id": function_call.call_identifier, "content": response}
		self.messages.append(new_message)
		
	def append_user_message(self, message):
		new_message = {"role": "user", "content": message}
		self.messages.append(new_message)

	def get_output(self, base_path):
		input_messages = self.messages.copy() #self.strip_assistant_content(self.messages)		
		# Transient system message
		input_messages.append({"role": "system", "content": AIModelQuerier.transient_prompt()})
				
		response_message = self.get_next_response_from_context()
		if response_message is not None:
			print(f"***Using response from context: {response_message.get('content')}")
		else:
			response = openai.ChatCompletion.create(
				model=self.model_identifier,
				max_tokens=1000,
				messages=input_messages,
				tools=self.get_tools(),
				# function_call={"name": "run_debugger_command"},
				stream=True
			)

			# create variables to collect the stream of chunks
			collected_chunks = []
			
			printed_response_header = False
			# iterate through the stream of events
			for chunk in response:
				collected_chunks.append(chunk.choices[0])  # save the event response
				chunk_message = chunk['choices'][0]  # extract the message
				
				if chunk_message.delta.get("content"):
					if not printed_response_header:
						print("***Streamed response from model: ", end = "")
						printed_response_header = True
					print(colored(chunk_message.delta.content, 'red'), end = "", flush=True)

			if printed_response_header:
				print("")
			# print(f"collected chunks: {collected_chunks}")
			# print the time delay and text received
			response_message = self.merge_chunks(collected_chunks)			
		
		# Extract the generated code
		self.messages.append(response_message)
		self.save_context(self._output_context_identifier)
		interimUUID = uuid.uuid4()
		self.save_context(interimUUID)
		print(colored(f"Saved interim state as {interimUUID}", 'light_grey'))
		# print(response_message)

		function_calls = []
		if response_message.get("tool_calls"):
			for tool_call in response_message["tool_calls"]:
				function_call = tool_call["function"]
				call_id = tool_call["id"]
				# print(f"***Function call: {function_call['name']}\n{function_call['arguments']}")
				function_name = function_call["name"]
				function_arguments = json.loads(function_call["arguments"])
				print(function_call)
				if function_name == "run_debugger_command":
					command = function_arguments["cmd"]
					function_calls.append(FunctionCall("lldb", function_name, call_id, command))
				elif function_name == "get_source":
					print(function_arguments)
					file_path = function_arguments["file_path"]
					line_number = function_arguments["line_number"]
					context_lines = function_arguments.get("context_lines", 10)
					context = f"{file_path}:{line_number}:{context_lines}"
					function_calls.append(FunctionCall("source", function_name, call_id, context))
				elif function_name == "modify_code":
					success, result = self.validate_changes_and_generate_unified_diff(function_arguments, base_path)
					print(function_arguments)
					if success:
						function_calls.append(FunctionCall("patch", function_name, call_id, result))			
					else:
						function_calls.append(FunctionCall("error", function_name, call_id,  f"Error generating diff for this change: {result}"))
				elif function_name == "restart":
					function_calls.append(FunctionCall("restart", function_name, call_id, None))
				else:
					function_calls.append(FunctionCall("none", function_name, call_id, None))			
		
		return function_calls
# 
# 		print(f"***Response:\n{response}")
# 		type, code = self.extract_code_and_type(response)
# 		print(f"***Extracted code of type {type}:\n{code}")
# 		return type, code
		
		# print(f"***Extracted solution:\n{solution}")
		# return LLMSolution(problem_input.problem_id, self.model_identifier, problem_input.prompt_id, solution)

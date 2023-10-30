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
			subclass = subclass_mapping.get(model_name, HumanAIModelQuerier)
			instances.append(subclass(model_name))
		return instances
	
	@classmethod
	def initial_prompt(cls):
		return "Act as a human who is using the lldb debugger to identify and fix crashes in a running process. You will be provided with output from lldb, and are able to issue commands to lldb to identify the issue. Before issuing a command, explain your reasoning about what command should be issued next and why it will help with the debugging of the process.\n\nUse the provided functions to issue lldb commands and make changes to the source code."#Issue only one command per message. Enclose that command in a Markdown code block. Do not include the (lldb) command-line prompt or anything else in the Markdown code block.\n\nOnce you have identified the problem, provide a patch that can be applied using the diff tool to fix the issue. Enclose the diff in a Markdown code block marked with 'diff'. Format the diff so that it can be applied directly via `patch -p0` applied in the same directory as the file paths are relative to."
		
		#\n\nThe debugger is already running and has stopped at the beginning of the program so that you can inspect the program and set breakpoints as necessary.\n\n
		
	def handle_debugger_output(cls, output):
		return self.get_output(output)

	def __str__(self) -> str:
		return f"{self.__class__.__name__}(model_identifier={self.model_identifier})"

class HumanAIModelQuerier(AIModelQuerier):	
	def get_output(self, input):
		prompt = input
		print("*** Human querier in use. Copy and paste the prompt below and provide it to the LLM. Provide the response, followed by an EOF character (ctrl-D).")
		print("*** PROMPT BEGIN")
		print(prompt)
		print("*** PROMPT END")
		
		# Copy to pasteboard
		process = subprocess.Popen('pbcopy', universal_newlines=True, stdin=subprocess.PIPE)
		process.communicate(prompt)
		process.wait()

		lines = []
		try:
			for line in sys.stdin:
				lines.append(line)
		except EOFError:
			pass
		response = "".join(lines)

		
		return response

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
		print(f"*** Initial prompt: {initial_prompt}")
		self.messages = [{"role": "system", "content": initial_prompt}]
		self._pending_context = []

		
	def load_context(self, context_identifier):
		self._pending_context = file_utilities.retrieve_context(context_identifier)
		
	def save_context(self, context_identifier):
		file_utilities.store_context(self.messages, context_identifier)
			
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

	def get_functions(self):
		return [
			{
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
			},
			{
				"name": "modify_code",
				"description": "Modify the source code.",
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
										}
									},
									"to-file-range": {
										"type": "object",
										"properties": {
											"start-line": {
												"type": "integer",
												"description": "The first line in the updated file that should be replaced. Line numbers start at 1.",
											},
											"code": {
												"type": "string",
												"description": "The code to replace the code in from-file-range.",
											}
										}
									},

								}
							}
						}
					},
					"required": ["file_path", "changes"]
				},
			},
			{
				"name": "compile",
				"description": "Compile the current version of the code.",
				"parameters": {
					"type": "object",
					"properties": {}
				}
			},
			{
				"name": "restart",
				"description": "Restart debugging from the beginning.",
				"parameters": {
					"type": "object",
					"properties": {}
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
		source_lines = source_code.splitlines(keepends=True)
		
		# Step 2: Generate the unified diff with context lines if changes are valid
		diffs = []
		
		for change in data["changes"]:
			# Determine the range of lines affected by this change
			start_line = change["from-file-range"]["start-line"] - 1
			end_line = start_line + len(change["from-file-range"]["code"].splitlines(keepends=True))
			
			# Extract the relevant lines from the source code
			from_code = [line.rstrip() for line in source_lines[max(0, start_line - context_lines):min(end_line + context_lines, len(source_lines))]]
			to_code = from_code.copy()
			
			# Apply the change to the to_code list, starting from the context lines before the change
			change_lines = [line.rstrip() for line in change["to-file-range"]["code"].splitlines(keepends=True)]
			change_start_index = start_line - max(0, start_line - context_lines)
			for i in range(len(change_lines)):
				to_code_index = change_start_index + i
				if to_code_index < len(to_code):
					to_code[to_code_index] = change_lines[i]
				else:
					to_code.append(change_lines[i])
			
			# Generate unified diff using difflib with context lines
			diff = difflib.unified_diff(
				from_code, 
				to_code, 
				fromfile=file_path, 
				tofile=file_path, 
				lineterm='',
				n=context_lines
			)
			
			diffs.extend(diff)
		
		# Return the patch
		return True, "\n".join(diffs)

	def generate_unified_diff(self, data, base_path):
		file_path = data["file_path"]
		diffs = []
	
		for change in data["changes"]:
			from_code = change["from-file-range"]["code"].splitlines(keepends=True)
			to_code = change["to-file-range"]["code"].splitlines(keepends=True)
			
			# Compute the correct start line for the unified diff using the provided start-line
			start_line = change["from-file-range"]["start-line"] - 1
			
			# Add context lines to correctly position the diff
			context_lines = ["\n" for _ in range(start_line)]
			from_code = context_lines + from_code
			to_code = context_lines + to_code
	
			# Generate unified diff using difflib without timestamps
			diff = difflib.unified_diff(
				from_code, 
				to_code, 
				fromfile=file_path, 
				tofile=file_path, 
				lineterm='',
				n=0
			)
			
			diffs.extend(diff)
	
		return "\n".join(diffs)

	def strip_assistant_content(self, data):
		for entry in data:
			if entry.get('role') == 'assistant' and 'content' in entry:
				entry['content'] = None
		return data		

	def get_next_response_from_context(self):
		response = None
		while len(self._pending_context) > 0 and response is None:
			next_message = self._pending_context[0]
			if next_message['role'] == 'assistant':
				response = next_message
			self._pending_context.pop(0)
		return response

	def get_output(self, input, base_path):
		prompt = input
		input_messages = self.strip_assistant_content(self.messages)
		print(f"***Prompt:\n{prompt}")
		# print(f"Input messages: {input_messages}")
		# Send the prompt to the OpenAI API
		self.messages.append({"role": "user", "content": prompt})
		
		response_message = self.get_next_response_from_context()
		if response_message is not None:
			print(f"***Using response from context")
		else:
			response = openai.ChatCompletion.create(
				model=self.model_identifier,
				max_tokens=1000,
				messages=input_messages,
				functions = self.get_functions()
			)
			response_message = response.choices[0].message
		
		# Extract the generated code
		self.messages.append(response_message)
		self.save_context("defg")
		# print(response)

		if response_message.get("content"):
			print(f"***Response:\n{response_message.get('content')}")
		
		if response_message.get("function_call"):
			function_call = response_message["function_call"]
			print(function_call)
			function_name = function_call["name"]
			function_arguments = json.loads(function_call["arguments"])
			if function_name == "run_debugger_command":
				command = function_arguments["cmd"]
				print(f"***Command: `{command}`")
				return "lldb", command
			elif function_name == "modify_code":
				success, result = self.validate_changes_and_generate_unified_diff(function_arguments, base_path)
				
				if success:					
					print(f"***Diff:\n{result}")
					return "diff", result
				else:
					print(f"***Diff generation error: {result}")
					return "error", result
			else:
				return function_name, None
		else:
			return "none", None
# 
# 		print(f"***Response:\n{response}")
# 		type, code = self.extract_code_and_type(response)
# 		print(f"***Extracted code of type {type}:\n{code}")
# 		return type, code
		
		# print(f"***Extracted solution:\n{solution}")
		# return LLMSolution(problem_input.problem_id, self.model_identifier, problem_input.prompt_id, solution)

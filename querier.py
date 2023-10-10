from abc import ABC, abstractmethod
from typing import List
import openai
import os
import sys
import subprocess
import re
import json
import difflib

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
		self.messages = [{"role": "user", "content": initial_prompt}]

			
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
												"type": "integer"
											},
											"code": {
												"type": "string"
											}
										}
									},
									"to-file-range": {
										"type": "object",
										"properties": {
											"start-line": {
												"type": "integer"
											},
											"code": {
												"type": "string"
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

	def get_output(self, input, base_path):
		prompt = input
		
		print(f"***Prompt:\n{prompt}")

		# Send the prompt to the OpenAI API
		self.messages.append({"role": "user", "content": prompt})
		response = openai.ChatCompletion.create(
			model=self.model_identifier,
			max_tokens=1000,
			messages=self.messages,
			functions = self.get_functions()
		)
		
		# Extract the generated code
		self.messages.append(response.choices[0].message)
		print(response)
		response_message = response.choices[0].message

		if response_message.get("function_call"):
			function_call = response_message["function_call"]
			
			function_name = function_call["name"]
			function_arguments = json.loads(function_call["arguments"])
			if function_name == "run_debugger_command":
				command = function_arguments["cmd"]
				print(f"Returning command {command}")
				return "lldb", command
			elif function_name == "modify_code":
				diff = self.generate_unified_diff(function_arguments, base_path)
				print(f"Returning diff {diff}")
				return "diff", diff
			else:
				return function_name, None
# 
# 		print(f"***Response:\n{response}")
# 		type, code = self.extract_code_and_type(response)
# 		print(f"***Extracted code of type {type}:\n{code}")
# 		return type, code
		
		# print(f"***Extracted solution:\n{solution}")
		# return LLMSolution(problem_input.problem_id, self.model_identifier, problem_input.prompt_id, solution)

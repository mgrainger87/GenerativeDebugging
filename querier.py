from abc import ABC, abstractmethod
from typing import List
import openai
import os
import sys
import subprocess
import re

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
		return "Act as a human who is debugging a process that sometimes crashes. You will do this with the lldb debugger. You will be provided with output from lldb, and are able to issue commands to lldb to identify the issue. If you would like, you can provide some commands before execution, or say \"run\" to begin."
		
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
			
	def is_chat_based_model(self):
		return "gpt-3.5" in self.model_identifier or "gpt-4" in self.model_identifier
	
	# def extract_code(self, response: str) -> str:
	# 	# Try to find the last Python code block
	# 	python_blocks = re.findall(r'``` ?python\n(.*?)\n```', response, re.DOTALL)
	# 	if python_blocks:
	# 		return python_blocks[-1].strip()
	# 	
	# 	# If no Python code block is found, try to find the last generic code block
	# 	generic_blocks = re.findall(r'``` ?\n(.*?)\n```', response, re.DOTALL)
	# 	if generic_blocks:
	# 		return generic_blocks[-1].strip()
	# 	
	# 	return response

	def get_output(self, input):
		prompt = AIModelQuerier.construct_textual_prompt(problem_input)
		
		# Add additional instructions for automated prompting
		# prompt += "\n\nAfter analyzing the problem, provide your solution in a Markdown code block. Do not include tests in the Markdown code block. The last Markdown code block in your response will be directly executed for testing."
		
		print(f"***Prompt:\n{prompt}")

		# Send the prompt to the OpenAI API
		if self.is_chat_based_model():
			messages = [{"role": "user", "content": prompt}]
			response = openai.ChatCompletion.create(
				model="gpt-4",
				max_tokens=1000,
				messages = messages)
			
			# Extract the generated code
			response = response.choices[0].message.content
			
		else:		
			response = openai.Completion.create(
				engine=self.model_identifier,
				prompt=prompt,
				max_tokens=1000
			)
			
			# Extract the generated code
			response = response.choices[0].text

		print(f"***Response:\n{response}")
		# solution = self.extract_code(response)
		return response
		
		# print(f"***Extracted solution:\n{solution}")
		# return LLMSolution(problem_input.problem_id, self.model_identifier, problem_input.prompt_id, solution)

import file_utilities
from abc import ABC, abstractmethod
import sys
import textwrap
from termcolor import colored

class GlobalContext:
	def __init__(self, workingDirectory, compileCommand, modelQuerier):
		self.workingDirectory = workingDirectory
		self.compileCommand = compileCommand	
		self.modelQuerier = modelQuerier

class CommandCenter:
	def __init__(self, modelQuerier, workingDirectory, compileCommand):
		self.modelQuerier = modelQuerier
		self.globalContext = GlobalContext(workingDirectory, compileCommand, modelQuerier)
	
	def on_stop(self, debug_session):
		command_output = debug_session.stop_info()
		self.modelQuerier.append_user_message(command_output)
		self.globalContext.debugSession = debug_session
		
		# Process the stop information or print it
		# print(stop_info)
		while True:
			if debug_session.has_exited():
				self.modelQuerier.append_user_message(f"The process exited with code {debug_session.exit_status_code()}.")
				file_utilities.store_success_sentinel(self.globalContext.workingDirectory)
				file_utilities.store_json_context(self.globalContext.workingDirectory, self.modelQuerier.messages)
				file_utilities.add_commit(self.globalContext.workingDirectory, f"Final commit after process exited with code {debug_session.exit_status_code()}.")
				break
			if self.modelQuerier.gave_up:
				break

			function_calls = self.modelQuerier.get_output(self.globalContext.workingDirectory)

			for function_call in function_calls:
				cmd = Command.get_command_object(function_call.type, function_call.context, self.globalContext)
				cmd.run()
				
				printable_context = '\n' + colored(textwrap.indent(function_call.context, '\t'), 'blue') if function_call.context else "(none)"
				command_output = cmd.command_output
				if len(command_output.strip()) == 0:
					command_output = "The command produced no output."
				print(f"***Command from model: {colored(function_call, 'red')}\n\tcontext: {printable_context}\n\tsuccess: {cmd.success}\n\tOutput: {colored(command_output, 'green')}")
				self.modelQuerier.append_function_call_response(function_call, command_output)
				
			file_utilities.store_json_context(self.globalContext.workingDirectory, self.modelQuerier.messages)
			
			

				
class Command(ABC):
	def __init__(self, context, globalContext):
		self.context = context
		self.globalContext = globalContext
		self.success = False
		self.command_output = ""

	@staticmethod
	def get_command_object(type, context, globalContext):
		if type == "patch":
			return PatchCommand(context, globalContext)
		elif type == "lldb":
			return DebuggerCommand(context, globalContext)
		elif type == "source":
			return SourceCommand(context, globalContext)
		elif type == "compile":
			return CompileCommand(context, globalContext)
		elif type == "restart":
			return RestartCommand(context, globalContext)
		elif type == "give_up":
			return GiveUpCommand(context, globalContext)
		elif type == "error":
			return ErrorCommand(context, globalContext)
		elif type == "none":
			return NoCommand(context, globalContext)
		else:
			raise ValueError(f"Unsupported command type: {type}")

	@abstractmethod
	def run(self):
		pass

class PatchCommand(Command):
	def run(self):
		self.success, command_output = file_utilities.apply_patch_from_string(self.globalContext.workingDirectory, self.context)
		
		if self.success:
			
			self.command_output = f"The patch was applied."
			
			compileCommand = CompileCommand({}, self.globalContext)
			compileCommand.run()
			self.success = compileCommand.success
			if self.success:
				file_utilities.add_commit(self.globalContext.workingDirectory, "Applying patch from model.")
				restartCommand = RestartCommand({}, self.globalContext)
				restartCommand.run()
				self.success = restartCommand.success
				self.command_output = f"{self.command_output}\n{restartCommand.command_output}"
			else:
				file_utilities.reset_to_last_commit(self.globalContext.workingDirectory)
				self.command_output = f"{self.command_output}\nCompilation failed: {compileCommand.command_output}. The patch was rolled back. For debugging purposes, the patch applied appears below:\n{self.context}"
			
		else:
			self.command_output = f"Applying the patch failed.\nPatch:\n{self.context}\n\nError: {command_output}"

class DebuggerCommand(Command):
	def run(self):
		self.success, command_output = self.globalContext.debugSession.execute_command(self.context)
		if self.success:
			self.command_output = command_output
		else:
			self.command_output = f"Command execution failed: {command_output}"

class SourceCommand(Command):
	def run(self):
		def prepend_line_numbers(text):
			lines = text.splitlines()  # Split the text into lines
			numbered_lines = [f"{i + 1}: {line}" for i, line in enumerate(lines)]  # Prepend line numbers
			return "\n".join(numbered_lines)  # Join the lines back into a single string

		def get_line_with_context(text, line_number, context):
			# Split the text into lines
			lines = text.split('\n')
		
			# Check if the line number is valid
			if line_number < 1 or line_number > len(lines):
				return "Line number out of range."
		
			# Adjust line number to 0-indexed
			line_number -= 1
		
			# Calculate the start and end indices for context
			start = max(0, line_number - context)
			end = min(len(lines), line_number + context + 1)
		
			# Extract the lines and join them back into a string
			return '\n'.join(lines[start:end])

		split_context = self.context.split(":")
		file_name = split_context[0]
		line_number = int(split_context[1])
		context_lines = int(split_context[2])
		
		self.command_output = file_utilities.get_source_code(self.globalContext.workingDirectory, file_name)
		
		if self.command_output:
			self.command_output = prepend_line_numbers(self.command_output)
			self.command_output = get_line_with_context(self.command_output, line_number, context_lines)

		else:
			self.success = False
			self.command_output = f"Failed to get contents of source file {self.context}."

class CompileCommand(Command):
	def run(self):
		returncode, stdout, stderr = file_utilities.execute_command(self.globalContext.workingDirectory, *self.globalContext.compileCommand)
		self.success = (returncode == 0)
		if not self.success:
			self.command_output = f"Compilation failed: {stdout} {stderr}"

class RestartCommand(Command):
	def run(self):
		self.success, self.command_output = self.globalContext.debugSession.restart()
		
class GiveUpCommand(Command):
	def run(self):
		self.globalContext.modelQuerier.append_user_message(f"The model gave up.")
		file_utilities.store_json_context(self.globalContext.workingDirectory, self.globalContext.modelQuerier.messages)
		file_utilities.store_failure_sentinel(self.globalContext.workingDirectory)
		file_utilities.add_commit(self.globalContext.workingDirectory, f"Final commit after the model gave up.")
		self.globalContext.modelQuerier.gave_up = True
		self.success = True
		self.command_output = "The model gave up."


class ErrorCommand(Command):
	def run(self):
		self.success = False
		self.command_output = self.context

class NoCommand(Command):
	def run(self):
		self.success = False
		self.command_output = f"You did not provide a command to run. Please provide a command."

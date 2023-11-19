import file_utilities
from abc import ABC, abstractmethod
import sys
import textwrap
from termcolor import colored

class GlobalContext:
	def __init__(self, workingDirectory, compileCommand):
		self.workingDirectory = workingDirectory
		self.compileCommand = compileCommand	

class CommandCenter:
	def __init__(self, modelQuerier, workingDirectory, compileCommand):
		self.modelQuerier = modelQuerier
		self.globalContext = GlobalContext(workingDirectory, compileCommand)
	
	def on_stop(self, debug_session):
		stop_info = debug_session.stop_info()
		
		# FIXME
		self.globalContext.debugSession = debug_session
		
		# Process the stop information or print it
		# print(stop_info)
		type, context = self.modelQuerier.get_output(stop_info, self.globalContext.workingDirectory)
		while True:
			cmd = Command.get_command_object(type, context, self.globalContext)
			cmd.run()
			
			printable_context = '\n' + colored(textwrap.indent(context, '\t'), 'blue') if context else "(none)"
			command_output = cmd.command_output
			if len(command_output.strip()) == 0:
				command_output = "The command produced no output."
			print(f"***Command from model: {colored(type, 'red')}\n\tcontext: {printable_context}\n\tsuccess: {cmd.success}\n\tOutput: {colored(command_output, 'green')}")
			# print(f"State: {debug_session.process.GetState()}")
			# print(f"Output: \"{command_output}\"")
			# print(f"Stripped: {command_output.strip()}")
			type, context = self.modelQuerier.get_output(command_output, self.globalContext.workingDirectory)
			

				
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
		elif type == "compile":
			return CompileCommand(context, globalContext)
		elif type == "restart":
			return RestartCommand(context, globalContext)
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
			self.command_output = f"{self.command_output}\n\n{compileCommand.command_output}"

			if self.success:
				restartCommand = RestartCommand({}, self.globalContext)
				restartCommand.run()
				self.success = restartCommand.success
				self.command_output = f"{self.command_output}\n\n{restartCommand.command_output}"
			
		else:
			self.command_output = f"Applying the patch failed.\nPatch:\n{self.context}\n\nError: {command_output}"

class DebuggerCommand(Command):
	def run(self):
		self.success, command_output = self.globalContext.debugSession.execute_command(self.context)
		if self.success:
			self.command_output = command_output
		else:
			self.command_output = f"Command execution failed: {command_output}"

class CompileCommand(Command):
	def run(self):
		returncode, stdout, stderr = file_utilities.execute_command(self.globalContext.workingDirectory, *self.globalContext.compileCommand)
		self.success = (returncode == 0)
		if not self.success:
			self.command_output = f"Compilation failed: {stdout} {stderr}"

class RestartCommand(Command):
	def run(self):
		self.success, self.command_output = self.globalContext.debugSession.restart()

class ErrorCommand(Command):
	def run(self):
		self.success = False
		self.command_output = self.context

class NoCommand(Command):
	def run(self):
		self.success = False
		self.command_output = f"You did not provide a command to run. Please provide a command."

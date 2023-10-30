import file_utilities
from abc import ABC, abstractmethod
import sys
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
			print(f"***Command: {colored(type, 'red')}\n\tcontext: {colored(context, 'blue')}\n\tsuccess: {cmd.success}\n\tOutput: {colored(cmd.command_output, 'green')}")
			# print(f"State: {debug_session.process.GetState()}")
			print(f"Stripped: {cmd.command_output.strip()}")
			if len(cmd.command_output.strip()) == 0:
				command_output = "The command produced no output."
			type, context = self.modelQuerier.get_output(cmd.command_output, self.globalContext.workingDirectory)
			

				
class Command(ABC):
	def __init__(self, context, globalContext):
		self.context = context
		self.globalContext = globalContext
		self.success = False
		self.command_output = ""

	@staticmethod
	def get_command_object(type, context, globalContext):
		if type == "diff":
			return DiffCommand(context, globalContext)
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

class DiffCommand(Command):
	def run(self):
		self.success, command_output = file_utilities.apply_patch_from_string(self.globalContext.workingDirectory, self.context)
		
		if self.success:
			self.command_output = f"The patch was applied."
		else:
			self.command_output = f"Applying the patch failed: {command_output}"

class DebuggerCommand(Command):
	def run(self):
		self.success, command_output = self.globalContext.debugSession.execute_command(self.context)
		if self.success:
			self.command_output = command_output
		else:
			self.command_output = f"Command execution failed: {command_output}"

class CompileCommand(Command):
	def run(self):
		# FIXME: success and output
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
		self.success = True
		print("The LLM had no further commands.")
		sys.exit(1)
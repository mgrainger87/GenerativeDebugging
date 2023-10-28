import file_utilities
from abc import ABC, abstractmethod

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
		type, context = self.modelQuerier.get_output(stop_info, self.globalContext.compileCommand)
		while True:
			cmd = Command.get_command_object(type, context, self.globalContext)
			cmd.run()
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
		else:
			raise ValueError(f"Unsupported command type: {type}")

	@abstractmethod
	def run(self):
		pass

class DiffCommand(Command):
	def run(self):
		print(f"self.context: {self.context}")
		self.success, command_output = file_utilities.apply_patch_from_string(self.globalContext.workingDirectory, self.context)
		
		if self.success:
			self.command_output = f"The patch was applied."
		else:
			self.command_output = f"Applying the patch failed: {command_output}"

class DebuggerCommand(Command):
	def run(self):
		self.success, command_output = self.globalContext.debugSession.execute_command(self.context)
		if not self.success:
			self.command_output = f"Command execution failed: {command_output}"

class CompileCommand(Command):
	def run(self):
		# FIXME: success and output
		file_utilities.execute_command(self.globalContext.workingDirectory, *self.globalContext.compileCommand)
		self.success = True

class RestartCommand(Command):
	def run(self):
		self.success, self.command_output = debug_session.restart()

class ErrorCommand(Command):
	def run(self):
		self.success = False
		self.command_output = self.context

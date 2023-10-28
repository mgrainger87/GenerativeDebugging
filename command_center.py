import file_utilities

class CommandCenter:
	def __init__(self, modelQuerier, workingDirectory, compileCommand):
		self.modelQuerier = modelQuerier
		self.workingDirectory = workingDirectory
		self.compileCommand = compileCommand
	
	def on_stop(self, debug_session):
		stop_info = debug_session.stop_info()
		# Process the stop information or print it
		# print(stop_info)
		type, code = self.modelQuerier.get_output(stop_info, self.workingDirectory)
		while True:
			if type == "diff":
				success, command_output = file_utilities.apply_patch_from_string(self.workingDirectory, code)
				if success:
					command_output = f"The patch was applied."
				else:
					command_output = f"Applying the patch failed: {command_output}"
			elif type == "lldb":
				success, command_output = debug_session.execute_command(code)
				if not success:
					command_output = f"Command execution failed: {command_output}"
			elif type == "compile":
				file_utilities.execute_command(self.workingDirectory, *self.compile_command)
			elif type == "restart":
				success, command_output = debug_session.restart()
			elif type == "error":
				command_output = code
			if len(command_output.strip()) == 0:
				command_output = "The command produced no output."
				# print(command_output)
			type, code = self.modelQuerier.get_output(command_output, self.workingDirectory)
				# print(command)

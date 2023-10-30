import lldb
import threading

class DebuggingSession:
	def __init__(self, executable_path, args=[]):
		self.executable_path = executable_path
		self.args = args

		self.debugger = lldb.SBDebugger.Create()
		self.debugger.SetAsync(True)
		self.target = self.debugger.CreateTarget(executable_path)
		if not self.target:
			raise Exception(f"Failed to create target for executable {executable_path}")

	def start(self, pause_at_start=False, entry_function_name="main", stop_handler=None, working_directory=None):
		self.stop_handler = stop_handler  # Store the stop_handler
	
		if pause_at_start:
			# Set a breakpoint at the entry function using the API
			self.target.BreakpointCreateByName(entry_function_name)
	
		launch_info = lldb.SBLaunchInfo(self.args)
	
		# Set the working directory if provided
		if working_directory:
			launch_info.SetWorkingDirectory(working_directory)
	
		error = lldb.SBError()
		self.__process = self.target.Launch(launch_info, error)
		if not error.Success():
			raise Exception(f"Failed to launch process: {error.GetCString()}")
	
		self.event_thread = threading.Thread(target=self.event_handler)
		self.event_thread.start()

	@property
	def process(self):
		"""Public property to get the SBProcess."""
		return self.__process
		
	def execute_command(self, command_str):
		command_interpreter = self.debugger.GetCommandInterpreter()
		# command_interpreter.HandleCommand('settings set auto-confirm 1', lldb.SBCommandReturnObject())
		result = lldb.SBCommandReturnObject()
		command_interpreter.HandleCommand(command_str, result)
		
		if result.Succeeded():
			return True, result.GetOutput()
		else:
			return False, result.GetError()
	
	def restart(self):
		# 1. Terminate the current process if it's running.
		if self.process.IsValid() and self.process.GetState() != lldb.eStateExited:
			self.process.Kill()
		
		# 2. Create a new target.
		self.target = self.debugger.CreateTarget(self.executable_path)
		if not self.target:
			return False, f"Failed to create target for executable {self.executable_path}"
		
		# 3. Launch the new process.
		launch_info = lldb.SBLaunchInfo(self.args)
		error = lldb.SBError()
		self.__process = self.target.Launch(launch_info, error)
		if not error.Success():
			return False, f"Failed to launch process: {error.GetCString()}"
		
		# Continue the debugging session as per the previous state.
		self.event_thread = threading.Thread(target=self.event_handler)
		self.event_thread.start()
		return True, "Process restarted successfully."

	def event_handler(self):
		listener = self.debugger.GetListener()
		event = lldb.SBEvent()
		while listener.WaitForEvent(1, event):
			if lldb.SBProcess.EventIsProcessEvent(event):
				state = lldb.SBProcess.GetStateFromEvent(event)
				if state == lldb.eStateStopped:
					if self.stop_handler:
						self.stop_handler(self)  # Call the stop_handler
				elif state == lldb.eStateExited:
					print("Program exited.")
					break
					
	def stop_info(self):
		process = self.process
		output_lines = []
		
		# Get the stopped thread
		thread = process.GetSelectedThread()
		queue_name = thread.GetQueueName() if thread.GetQueueName() else '<no queue>'
		output_lines.append(f"* thread #{thread.GetIndexID()}, queue = '{queue_name}', stop reason = {thread.GetStopDescription(100)}")
		
		# Get the frames of the stopped thread
		for frame in thread:
			function_name = frame.GetFunctionName()
			line_entry = frame.GetLineEntry()
			file_spec = line_entry.GetFileSpec()
			file_name = file_spec.GetFilename()
			load_address = frame.GetPC()
		
			# Format the load address as a hexadecimal string
			load_address_hex = f"0x{load_address:016x}"
		
			# Get the module name
			module = frame.GetModule()
			module_name = module.GetFileSpec().GetFilename()
		
			# Get the offset within the function
			offset = frame.GetPC() - frame.GetSymbol().GetStartAddress().GetLoadAddress(self.target)
		
			if file_name:
				output_lines.append(f"  * frame #{frame.GetFrameID()}: {load_address_hex} {module_name}`{function_name} at {file_name}:{line_entry.GetLine()}:{line_entry.GetColumn()}")
			else:
				# For frames without file information, include the offset within the function
				output_lines.append(f"    frame #{frame.GetFrameID()}: {load_address_hex} {module_name}`{function_name} + {offset}")
		
		return '\n'.join(output_lines)

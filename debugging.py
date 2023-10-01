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

	def start(self, pause_at_start=False, entry_function_name="main", stop_handler=None):
		self.stop_handler = stop_handler  # Store the stop_handler
		
		if pause_at_start:
			# Set a breakpoint at the entry function using the API
			self.target.BreakpointCreateByName(entry_function_name)
			
		launch_info = lldb.SBLaunchInfo(self.args)
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
		result = lldb.SBCommandReturnObject()
		command_interpreter.HandleCommand(command_str, result)
		return result.Succeeded(), result.GetOutput()
	
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
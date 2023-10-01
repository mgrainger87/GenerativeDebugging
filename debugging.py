import lldb
import signal
import os
import threading

class DebuggingSession:
	def __init__(self, executable_path, args=[], stop_handler=None):
		self.__executable_path = executable_path
		self.__args = args
		self.__stop_handler = stop_handler
	
		self.__debugger = lldb.SBDebugger.Create()
		self.__debugger.SetAsync(True)
		self.__target = self.__debugger.CreateTarget(executable_path)
		if not self.__target:
			raise Exception(f"Failed to create target for executable {executable_path}")
	
		launch_info = lldb.SBLaunchInfo(args)
		error = lldb.SBError()
		self.__process = self.__target.Launch(launch_info, error)
		if not error.Success():
			raise Exception(f"Failed to launch process: {error.GetCString()}")
	
		self.__listener = self.__debugger.GetListener()
		self.__event_thread = threading.Thread(target=self.event_handler)
		self.__event_thread.start()

	def execute_command(self, command_str):
		command_interpreter = self.__debugger.GetCommandInterpreter()
		result = lldb.SBCommandReturnObject()
		command_interpreter.HandleCommand(command_str, result)
		return result.Succeeded(), result.GetOutput()
	
	def set_breakpoint(self, file, line):
		breakpoint = self.__target.BreakpointCreateByLocation(file, line)
		return breakpoint.GetID()

	def delete_breakpoint(self, breakpoint_id):
		return self.__target.BreakpointDelete(breakpoint_id)

	def list_breakpoints(self):
		breakpoints = []
		for i in range(self.__target.GetNumBreakpoints()):
			breakpoint = self.__target.GetBreakpointAtIndex(i)
			location = breakpoint.GetLocationAtIndex(0)
			file = location.GetFileSpec().GetFilename()
			line = location.GetLineEntry().GetLine()
			breakpoints.append((breakpoint.GetID(), file, line))
		return breakpoints

	def event_handler(self):
		event = lldb.SBEvent()
		while self.__listener.WaitForEvent(1, event):
			if lldb.SBProcess.EventIsProcessEvent(event):
				state = lldb.SBProcess.GetStateFromEvent(event)
				if state == lldb.eStateStopped:
					if self.__stop_handler:
						self.__stop_handler(self)  # pass the DebuggingSession instance to the handler
				elif state == lldb.eStateExited:
					print("Program exited.")
					break

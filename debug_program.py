import argparse
import querier
import debugging
from functools import partial
import file_utilities
import os

class HandlerClass:
	def __init__(self, modelQuerier, workingDirectory):
		self.modelQuerier = modelQuerier
		self.workingDirectory = workingDirectory
	
	def on_stop(self, debug_session):
		stop_info = self.get_stop_info(debug_session)
		# Process the stop information or print it
		# print(stop_info)
		type, code = self.modelQuerier.get_output(stop_info)
		while True:
			if type == "diff":
				success, command_output = file_utilities.apply_patch_from_string(self.workingDirectory, code)
				if success:
					command_output = f"The patch was applied."
				else:
					command_output = f"Applying the patch failed: {command_output}"
			else:
				success, command_output = debug_session.execute_command(code)
				if not success:
					command_output = f"Command execution failed: {command_output}"
			if len(command_output.strip()) == 0:
				command_output = "The command produced no output."
				# print(command_output)
			type, code = self.modelQuerier.get_output(command_output)
				# print(command)
	
	def get_stop_info(self, debug_session):
		process = debug_session.process
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
			offset = frame.GetPC() - frame.GetSymbol().GetStartAddress().GetLoadAddress(debug_session.target)
		
			if file_name:
				output_lines.append(f"  * frame #{frame.GetFrameID()}: {load_address_hex} {module_name}`{function_name} at {file_name}:{line_entry.GetLine()}:{line_entry.GetColumn()}")
			else:
				# For frames without file information, include the offset within the function
				output_lines.append(f"    frame #{frame.GetFrameID()}: {load_address_hex} {module_name}`{function_name} + {offset}")
		
		return '\n'.join(output_lines)
				
def main():
	parser = argparse.ArgumentParser(description="Run specified phases of the grading process.")
	parser.add_argument('--code_path', required=True, help=f"The directory containing the code. This directory will be copied before compilation and execution.")
	parser.add_argument('--compile_command', required=True, help=f"The command to run to compile the code. This command will be run with the code path as the current working directory.")
	parser.add_argument('--executable', required=True, help=f"The executable to run, relative to the code directory.")
	parser.add_argument('--model', required=True, help=f"The model(s) to use debugging the program. The following model names can be queried through the OpenAI API: {querier.OpenAIModelQuerier.supported_model_names()}")
	args = parser.parse_args()

	code_directory = file_utilities.copy_to_temp(args.code_path)
	print(f"Copied code to {code_directory}")
	file_utilities.execute_command(code_directory, args.compile_command)
	print(f"Compiled with {args.compile_command}")
	executable_path = os.path.join(code_directory, args.executable)
	print(f"Running {executable_path}…")

	modelQuerier = querier.AIModelQuerier.resolve_queriers([args.model])[0]	
	handler = HandlerClass(modelQuerier, code_directory)
	
	session = debugging.DebuggingSession(executable_path)
	session.start(stop_handler=handler.on_stop, pause_at_start=False)

if __name__ == "__main__":
	main()

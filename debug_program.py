import argparse
import querier
import debugging
from functools import partial

class HandlerClass:
	def __init__(self, modelQuerier):
		self.modelQuerier = modelQuerier
	
	def on_stop(self, debug_session):
		stop_info = self.get_stop_info(debug_session)
		# Process the stop information or print it
		print(stop_info)
		command = self.modelQuerier.get_output(stop_info)
		while True:
			command_output = debug_session.execute_command(command)
			print(command_output)
			command = self.modelQuerier.get_output(command_output)
			print(command)
		# success, output = debug_session.execute_command("bt")
	
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
	parser.add_argument('--executable', required=True, help=f"The executable to run.")
	parser.add_argument('--model', required=True, help=f"The model(s) to use debugging the program. The following model names can be queried through the OpenAI API: {querier.OpenAIModelQuerier.supported_model_names()}")
	args = parser.parse_args()

	modelQuerier = querier.AIModelQuerier.resolve_queriers([args.model])[0]	
	handler = HandlerClass(modelQuerier)

	session = debugging.DebuggingSession(args.executable)
	session.start(stop_handler=handler.on_stop, pause_at_start=True)
	print(session)

if __name__ == "__main__":
	main()

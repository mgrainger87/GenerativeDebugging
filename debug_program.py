import argparse
import querier
import debugging
from functools import partial
import file_utilities
import os
import command_center
				
def main():
	parser = argparse.ArgumentParser(description="Run specified phases of the grading process.")
	parser.add_argument('--code_path', required=True, help=f"The directory containing the code. This directory will be copied before compilation and execution.")
	parser.add_argument('--compile_command', nargs='*', required=True, help=f"The command to run to compile the code. This command will be run with the code path as the current working directory.")
	parser.add_argument('--executable', required=True, help=f"The executable to run, relative to the code directory.")
	parser.add_argument('--model', required=True, help=f"The model(s) to use debugging the program. The following model names can be queried through the OpenAI API: {querier.OpenAIModelQuerier.supported_model_names()}")
	parser.add_argument('--context_identifier', required=False, help=f"The stored context to resume from.")
	args = parser.parse_args()
	
	modelQuerier = querier.AIModelQuerier.resolve_queriers([args.model])[0]
	print(f"***Using context identifier {modelQuerier.get_context_identifier()}")

	code_directory = file_utilities.copy_to_temp(args.code_path)
	print(f"Copied code to {code_directory}")
	file_utilities.execute_command(code_directory, *args.compile_command)
	print(f"Compiled with {args.compile_command}")
	executable_path = os.path.join(code_directory, args.executable)
	print(f"Running {executable_path}…")

	commandCenter = command_center.CommandCenter(modelQuerier, code_directory, args.compile_command)
	if args.context_identifier:
		modelQuerier.load_context(args.context_identifier)
	
	session = debugging.DebuggingSession(executable_path)
	session.start(stop_handler=commandCenter.on_stop, pause_at_start=False, working_directory=code_directory)

if __name__ == "__main__":
	main()

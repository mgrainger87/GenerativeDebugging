import argparse
import querier
import debugging
from functools import partial
import file_utilities
import os
import command_center
from termcolor import colored

def gprint(input_str):
	print(colored(input_str, 'light_grey'))
			
def main():
	parser = argparse.ArgumentParser(description="Run specified phases of the grading process.")
	parser.add_argument('--code_path', required=True, help=f"The directory containing the code. This directory will be copied before compilation and execution.")
	parser.add_argument('--compile_command', nargs='*', required=True, help=f"The command to run to compile the code. This command will be run with the code path as the current working directory.")
	parser.add_argument('--executable', required=True, help=f"The executable to run, relative to the code directory.")
	parser.add_argument('--model', required=True, help=f"The model(s) to use debugging the program. The following model names can be queried through the OpenAI API: {querier.OpenAIModelQuerier.supported_model_names()}")
	parser.add_argument('--context_identifier', required=False, help=f"The stored context to resume from.")
	args = parser.parse_args()
	
	modelQuerier = querier.AIModelQuerier.resolve_queriers([args.model])[0]
	gprint(f"***Using context identifier {modelQuerier.get_context_identifier()}")

	code_directory = file_utilities.copy_to_temp(args.code_path)
	gprint(f"Copied code to {code_directory}")
	file_utilities.execute_command(code_directory, *args.compile_command)
	gprint(f"Compiled with {args.compile_command}")
	executable_path = os.path.join(code_directory, args.executable)
	gprint(f"Running {executable_path}…")

	commandCenter = command_center.CommandCenter(modelQuerier, code_directory, args.compile_command)
	if args.context_identifier:
		modelQuerier.load_context(args.context_identifier)
	
	session = debugging.DebuggingSession(executable_path)
	session.start(pause_at_start=False, working_directory=code_directory)
	
	while True:
		gprint(f"Process status: {session.process}")
		if session.has_exited():
			print(f"Process exited with return code {session.exit_status_code()}")
			break
		commandCenter.on_stop(session)

if __name__ == "__main__":
	main()

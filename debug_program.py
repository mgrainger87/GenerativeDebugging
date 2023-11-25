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

def debug_executable(code_path, compile_command, executable, model, context_identifier, output_path):
	modelQuerier = querier.AIModelQuerier.resolve_queriers([model])[0]
	gprint(f"***Using context identifier {modelQuerier.get_context_identifier()}")
	
	code_directory = file_utilities.copy_to_temp(code_path)
	file_utilities.initialize_git_repository(code_directory)
	gprint(f"Copied code to {code_directory}")	
	
	file_utilities.execute_command(code_directory, *compile_command)
	gprint(f"Compiled with {compile_command}")
	executable_path = os.path.join(code_directory, executable)
	gprint(f"Running {executable_path}…")
	
	commandCenter = command_center.CommandCenter(modelQuerier, code_directory, compile_command)
	if context_identifier:
		modelQuerier.load_context(context_identifier)
	
	session = debugging.DebuggingSession(executable_path)
	session.start(pause_at_start=False, working_directory=code_directory)
	
	while True:
		gprint(f"Process status: {session.process}")
		if session.has_exited():
			print(f"Process exited with return code {session.exit_status_code()}")
			break
		commandCenter.on_stop(session)
		
	# Copy git repository to the output directory
	if output_path:
		file_utilities.copy_dir(code_directory, output_path)

def main():
	parser = argparse.ArgumentParser(description="Run specified phases of the grading process.")
	parser.add_argument('--code_path', required=False, help=f"The directory containing the code. This directory will be copied before compilation and execution.")
	parser.add_argument('--code_directory_path', required=False, help=f"A directory containing multiple directories, one for each executable to be debugged.")
	parser.add_argument('--compile_command', nargs='*', required=True, help=f"The command to run to compile the code. This command will be run with the code path as the current working directory.")
	parser.add_argument('--executable', required=True, help=f"The executable to run, relative to the code directory.")
	parser.add_argument('--model', required=True, help=f"The model(s) to use debugging the program. The following model names can be queried through the OpenAI API: {querier.OpenAIModelQuerier.supported_model_names()}")
	parser.add_argument('--context_identifier', required=False, help=f"The stored context to resume from.")
	parser.add_argument('--output_path', required=False, help=f"The path to store completed git repositories at.")
	args = parser.parse_args()
	
	if args.code_path:
		debug_executable(args.code_path, args.compile_command, args.executable, args.model, args.context_identifier, args.output_path)
	elif args.code_directory_path:
		if not os.path.exists(args.code_directory_path):
			print(f"The directory '{args.code_directory_path}' does not exist.")
			return
			
		context_identifier = args.context_identifier
		# Iterate over the entries in the directory
		for entry in os.listdir(args.code_directory_path):
			# Construct the full path
			full_path = os.path.join(args.code_directory_path, entry)
			
			# Check if the entry is a directory
			if os.path.isdir(full_path):
				print(full_path)
				
				output_path = None
				if args.output_path:
					output_path = os.path.join(args.output_path, entry)
					
					if os.path.exists(output_path) and os.path.isdir(output_path) and os.listdir(output_path):
						print(f"Skipping debugging for {entry} since its output directory already exists")
						continue
				
					if not os.path.exists(output_path):
						# Create the directory, including any intermediate directories
						os.makedirs(output_path)
				
				gprint(f"Starting debugging process for {entry}…")
				debug_executable(full_path, args.compile_command, args.executable, args.model, context_identifier, output_path)
				
				# Assume that the context identifier is intended to be used only for the first program, since they aren't transferrable across programs being debugged.
				context_identifier = None

if __name__ == "__main__":
	main()

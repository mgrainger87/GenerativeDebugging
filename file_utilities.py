import shutil
import tempfile
import os
import subprocess
import pickle
import json

def copy_to_temp(source_dir):
	# Create a temporary directory
	temp_dir = tempfile.mkdtemp()
	
	# Copy the entire content of the source directory to the temporary directory
	for item in os.listdir(source_dir):
		s = os.path.join(source_dir, item)
		d = os.path.join(temp_dir, item)
		if os.path.isdir(s):
			shutil.copytree(s, d)
		else:
			shutil.copy2(s, d)
			
	return temp_dir

def execute_command(directory_path, command, *args):
	"""
	Execute a command in a specified directory.

	:param directory_path: The directory in which the command should be executed.
	:param command: The command to execute.
	:param args: Additional arguments to pass to the command.
	:return: A tuple containing the return code, stdout, and stderr.
	"""
	full_command = [command] + list(args)
	
	result = subprocess.run(full_command, cwd=directory_path, text=True, capture_output=True)
	
	return result.returncode, result.stdout, result.stderr
	
def apply_patch_from_string(working_directory, patch_string):
	try:
		# Dry run to check if the patch can be applied
		dry_run_process = subprocess.Popen(['patch', '-s', '-p0', '--dry-run', '--batch'], cwd=working_directory, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		dry_run_stdout, dry_run_stderr = dry_run_process.communicate(input=patch_string.encode())

		if dry_run_process.returncode != 0:
			# Dry run failed, patch cannot be applied cleanly
			return (False, f'An error occurred ({dry_run_process.returncode}) when attempting to apply the patch: {dry_run_stdout.decode()} {dry_run_stderr.decode()}\n\nThe patch has not been applied.')

		# Actual patch application since dry run was successful
		process = subprocess.Popen(['patch', '-s', '-p0', '--batch'], cwd=working_directory, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout, stderr = process.communicate(input=patch_string.encode())

		# Print stdout and stderr
		if stdout:
			print("STDOUT:", stdout.decode())
		if stderr:
			print("STDERR:", stderr.decode())

		if process.returncode == 0:
			# Patch applied successfully
			return (True, None)
		else:
			# There was an error applying the patch
			return (False, f'{stdout.decode()} {stderr.decode()}')
	except Exception as e:
		# There was an error running the subprocess
		return (False, str(e))

def get_source_code(working_directory, file_path):
	try:
		full_path = os.path.join(working_directory, file_path)
		with open(full_path, 'r') as f:
			return f.read()
	except Exception as e:
		print(e)
		return None
		
# Define the base directory in the macOS cache location
BASE_DIR = os.path.join(os.path.expanduser('~'), 'Library', 'Caches', 'com.yourcompany.yourappname')
		

def get_file_path(context_id):
	"""Return the file path associated with the given context_id."""
	return os.path.join(BASE_DIR, f"{context_id}.pkl")

def store_context(context, context_id):
	"""Store the context to a file associated with the given context_id."""
	if not os.path.exists(BASE_DIR):
		os.makedirs(BASE_DIR)
	with open(get_file_path(context_id), 'wb') as f:
		pickle.dump(context, f)
		
def store_json_context(directory_path, context):
	with open(os.path.join(directory_path, 'conversation.json'), 'w') as f:
		f.write(json.dumps(context, indent=2))

def retrieve_context(context_id):
	"""Retrieve the context associated with the given context_id."""
	with open(get_file_path(context_id), 'rb') as f:
		return pickle.load(f)
		
def initialize_git_repository(directory_path):
	os.chdir(directory_path)
	
	# Initialize the Git repository
	subprocess.run(['git', 'init'])
	
	# Add all files to staging
	subprocess.run(['git', 'add', '.'])
	
	# Make the initial commit
	subprocess.run(['git', 'commit', '-m', 'Initial commit'])
	
def add_commit(directory_path, commit_message):
	os.chdir(directory_path)
	subprocess.run(['git', 'add', '.'])
	subprocess.run(['git', 'commit', '-m', commit_message])

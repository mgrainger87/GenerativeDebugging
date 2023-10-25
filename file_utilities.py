import shutil
import tempfile
import os
import subprocess
import pickle

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
	print(full_command)
	
	result = subprocess.run(full_command, cwd=directory_path, text=True, capture_output=True)
	
	return result.returncode, result.stdout, result.stderr

import subprocess
	
def apply_patch_from_string(working_directory, patch_string):
	try:        
		# Apply the patch using -p0, patch string is piped as input
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

def retrieve_context(context_id):
	"""Retrieve the context associated with the given context_id."""
	with open(get_file_path(context_id), 'rb') as f:
		return pickle.load(f)
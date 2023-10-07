import shutil
import tempfile
import os
import subprocess

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
		# Append EOF to the patch string
		patch_string_with_eof = patch_string + '\x04'  # \x04 is the EOF marker in ASCII
		
		# Apply the patch using -p0, patch string is piped as input
		process = subprocess.Popen(['patch', '-s', '-p0'], cwd=working_directory, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		_, error = process.communicate(input=patch_string_with_eof.encode())
		
		if process.returncode == 0:
			# Patch applied successfully
			return (True, None)
		else:
			# There was an error applying the patch
			return (False, error.decode())
	except Exception as e:
		# There was an error running the subprocess
		return (False, str(e))

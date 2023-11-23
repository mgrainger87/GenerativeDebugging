import os
import subprocess
import sys

def compile_and_run(file_path):
	# Determine the compiler to use based on file extension
	compiler = "clang++" if file_path.endswith('.cpp') else "clang"

	# Compile the file
	exe_path = f"{file_path}.exe"
	compile_process = subprocess.run([compiler, file_path, "-o", exe_path],
									 capture_output=True, text=True)
	if compile_process.returncode != 0:
		print(f"Compilation failed for {file_path}: {compile_process.stderr}")
		return False

	# Run the compiled executable
	run_process = subprocess.run([exe_path], capture_output=True, text=True)
	if run_process.returncode != 0:
		print(f"Executable crashed for {file_path}: {run_process.stderr}")
		return True
	else:
		print(f"Executable ran successfully for {file_path}")
		return False

def process_directory(directory):
	for root, dirs, files in os.walk(directory):
		for file in files:
			if file.endswith(('.c', '.cpp')):
				file_path = os.path.join(root, file)
				compile_and_run(file_path)

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print("Usage: python script.py <directory>")
		sys.exit(1)

	directory = sys.argv[1]
	process_directory(directory)

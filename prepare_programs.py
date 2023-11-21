import os
import subprocess
import re
import sys

def comment_remover(text):
	def replacer(match):
		s = match.group(0)
		if s.startswith('/'):
			return " "  # note: a space and not an empty string
		else:
			return s
	pattern = re.compile(
		r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
		re.DOTALL | re.MULTILINE
	)
	return re.sub(pattern, replacer, text)

def process_file(file_path, output_dir):
	# Run unifdef
	cmd = f"unifdef -DOMITGOOD -UOMITBAD -DINCLUDEMAIN {file_path}"
	result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
	if result.returncode != 0 and result.returncode != 1:
		print(f"Error processing {file_path}: {result.stdout} {result.stderr}")
		return

	# Remove comments
	cleaned_code = comment_remover(result.stdout)

	# Construct output file path
	rel_path = os.path.relpath(file_path, start=input_dir)
	output_file_path = os.path.join(output_dir, rel_path)

	# Create directory if it doesn't exist
	os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

	# Write the cleaned code to the output file
	with open(output_file_path, 'w') as file:
		file.write(cleaned_code)

def process_directory(input_dir, output_dir):
	for root, dirs, files in os.walk(input_dir):
		for file in files:
			if file.endswith(('.c', '.cpp', '.h')):
				file_path = os.path.join(root, file)
				process_file(file_path, output_dir)

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print(f"Usage: python {sys.argv[0]} <input_directory>")
		sys.exit(1)

	input_dir = sys.argv[1]
	output_dir = input_dir + '_processed'

	process_directory(input_dir, output_dir)

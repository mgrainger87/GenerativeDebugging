#! /usr/bin/env/python 3.0
#
# Modifies main.cpp and testcases.h to call all the test cases.
# Modified main_linux.cpp to call the non w32 test cases.
#
# Users should not use this file directly. Functions in this file are called
# by create_per_cwe_files.py, create_single_batch_file.py, and create_single_Makefile.py.
#

import sys
import os
import re
import shutil
import py_common
import subprocess

def build_list_of_primary_c_cpp_testcase_files(directory, testcaseregexes):

	files_to_check = []
	for root, dirs, files in os.walk(directory):
		for name in files:
			# if there are multiple files, we only want the "a" (or primary) one since that had the good and bad defined in it.  
			# In the C++ class related issues, we want only the bad since all we need is the namespace and both good and bad will be in the same namespace. (and we don't want to end up calling the good and bad more than once). 
			result = re.search(py_common.get_primary_testcase_filename_regex(), name, re.IGNORECASE)

			if result != None:
				if testcaseregexes == None:
					files_to_check.append(os.path.realpath(os.path.join(root,name)))
				else:
					for testcaseregex in testcaseregexes:
						if re.match('.*' + testcaseregex +'.*', name):
							files_to_check.append(os.path.realpath(os.path.join(root,name)))
			else:
				pass
				
		# if len(files_to_check) > 100:
		# 	break
				
		# don't enumerate files in support directories
		if 'testcasesupport' in dirs:
			dirs.remove('testcasesupport')

	return files_to_check

class TestCase:
	def __init__(self, name, file_path, function_name, file_extension, header_lines):
		self.name = name
		self.file_path = file_path
		self.function_name = function_name
		self.file_extension = file_extension
		self.header_lines = header_lines
		
	def __str__(self):
		return f"{self.name} // {self.file_path} // {self.function_name}  // {self.file_extension} // {self.header_lines}"

MAIN_FILE_TEMPLATE = """#include <time.h>
#include <stdlib.h>

<prototype>

int main(int argc, char * argv[]) {
	/* seed randomness */
	srand( (unsigned)time(NULL) );
	<function_call>
}
"""

MAKEFILE_TEMPLATE = """# Variables
CC = <compiler>
CFLAGS = -g
SOURCES = <source files>
TARGET = main

# Targets and Rules
all: $(TARGET)

$(TARGET): $(SOURCES)
	$(CC) $(CFLAGS) $(SOURCES) -o $(TARGET)

clean:
	rm -f $(TARGET)
"""

def write_test_case(testCase, base_path, copy_paths):
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

	subdir_path = os.path.join(base_path, testCase.name)
	os.makedirs(subdir_path, exist_ok=True)
	
	main_file_name = "main." + testCase.file_extension
	file_path = os.path.join(subdir_path, main_file_name)
	
	stripped_function_name = testCase.function_name.replace(testCase.name, 'func').replace('bad', 'foo')
	stripped_headers = testCase.header_lines.replace(testCase.name, 'func').replace('bad', 'foo')
	main_contents = MAIN_FILE_TEMPLATE.replace("<prototype>", stripped_headers).replace("<function_call>", stripped_function_name)
	
	with open(file_path, 'w') as file:
		file.write(main_contents)
	
	test_case_output_path = os.path.join(subdir_path, os.path.basename(testCase.file_path).replace(testCase.name, 'func'))
	
	# Run unifdef
	cmd = f"unifdef -DOMITGOOD -UOMITBAD -UINCLUDEMAIN -U_WIN32 {testCase.file_path}"
	result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
	if result.returncode != 0 and result.returncode != 1:
		print(f"Error processing {file_path}: {result.stderr}")
		return
	
	cleaned_code = comment_remover(result.stdout).replace(testCase.name, 'func').replace('bad', 'foo')
	with open(test_case_output_path, 'w') as file:
		file.write(cleaned_code)
	
	# Write other files
	for path in copy_paths:
		dest = os.path.join(subdir_path, os.path.basename(path))
		shutil.copy2(path, dest)

	all_source_files = []
	for file in os.listdir(subdir_path):
		if file.endswith('.c') or file.endswith('.cpp'):
			all_source_files.append(file)

	# Write Makefile
	compiler = "clang++" if testCase.file_extension == "cpp" else "clang"
	makefile_contents = MAKEFILE_TEMPLATE.replace("<source files>", " ".join(all_source_files)).replace("<compiler>", compiler)

	with open(os.path.join(subdir_path, "Makefile"), 'w') as file:
		file.write(makefile_contents)

def generate_test_cases(testcase_files):
	testCases = []
	for fullfilepath in testcase_files:

		filename = os.path.basename(fullfilepath)

		# we only want the non w32 and non wchar_t test cases
		if ('w32' not in filename) and ('wchar_t' not in filename):
			
			# do different things if its a c or cpp file
			match = re.search("^(?P<root>CWE(\d+).*__.*_\d+)((?P<letter>[a-z]*)|_(bad|good\d+))(\.c|\.cpp)$", filename)
			print(filename)

			if filename.endswith(".cpp"):
				root = match.group("root") # we don't use the letter in the namespace 
				bad = "bad();"

				function_name = root + "::" + bad
				header_lines = "\tnamespace " + root + " { void " + bad + "}\n"
				testCases.append(TestCase(root, fullfilepath, function_name, "cpp", header_lines))

			elif filename.endswith(".c"):
				# we only want to add the "a" files
				# if match.group("letter") != "" and match.group("letter") != "a":
				# 	print("Ignored file: " + filename)
				# 	continue
				root = match.group("root")
				bad = "_bad();"

				function_name = root + bad
				header_lines = "\tvoid " + root + bad + "\n"
				testCases.append(TestCase(root, fullfilepath, function_name, "c", header_lines))
			else:
				raise Exception("filename ends with something we don't handle!: " + fullfilepath)
	return testCases

def update_main_cpp_and_testcases_h(testcaseregexes):

	# get list of testcase files
	testcase_location = "/Users/morgang/Downloads/Juliet/testcases"
	testcase_files = build_list_of_primary_c_cpp_testcase_files(testcase_location, testcaseregexes)

	file_path = "testcasesupport/"
	testcases_dot_h = "testcases.h"

	# generate the lines that call the testcase fx's
	testCases = generate_test_cases(testcase_files)
	
	copy_files = [
		"io.c",
		"std_testcase_io.h",
		"std_testcase.h",
		"std_thread.h",
		"std_thread.c",
	]
	copy_files = [os.path.join("/Users/morgang/Downloads/Juliet/testcasesupport", p) for p in copy_files]
	for testCase in testCases:
		write_test_case(testCase, "/tmp/juliet", copy_files)
	
	return

def replace_subdirectories(source_dir, destination_dir):
	# Iterate through each subdirectory in the destination directory
	for item in os.listdir(destination_dir):
		dest_subdir = os.path.join(destination_dir, item)

		# Check if it's a directory and if the same directory exists in the source
		if os.path.isdir(dest_subdir) and os.path.exists(os.path.join(source_dir, item)):
			source_subdir = os.path.join(source_dir, item)

			# Remove the subdirectory from the destination
			shutil.rmtree(dest_subdir)

			# Copy the subdirectory from the source to the destination
			shutil.copytree(source_subdir, dest_subdir)
			print(f"Replaced subdirectory: {item}")
	
	# Example usage
	# replace_subdirectories('/path/to/source_dir', '/path/to/destination_dir')

if __name__ == "__main__":

	testcaseregexes=None

	if len(sys.argv) > 1:
		if sys.argv[1] == '-h':
			sys.stderr.write(f'Usage: {sys.argv[0]} (optional regexes of testcases)\n')
			sys.exit(1)
		testcaseregexes=sys.argv[1:]

	update_main_cpp_and_testcases_h(testcaseregexes)
	replace_subdirectories("/tmp/juliet", "/Users/morgang/code/GenerativeDebugging/juliet")

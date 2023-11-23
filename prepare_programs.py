import os
import subprocess
import re
import sys

HEADER_REPLACEMENT = """#define __STDC_LIMIT_MACROS 1

#define ALLOCA alloca

#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <time.h>
#include <limits.h>
#include <string.h>
#include <stdint.h>
#include <stdint.h>
#include <ctype.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>

#ifdef __cplusplus
#include <new>

class TwoIntsClass 
{
	public:
		int intOne;
		int intTwo;
};

class OneIntClass 
{
	public:
		int intOne;
};

#endif

#ifndef __cplusplus
#define true 1
#define false 0

#endif /* end ifndef __cplusplus */

#define URAND31() (((unsigned)rand()<<30) ^ ((unsigned)rand()<<15) ^ rand())
#define RAND32() ((int)(rand() & 1 ? URAND31() : -URAND31() - 1))

#define URAND63() (((uint64_t)rand()<<60) ^ ((uint64_t)rand()<<45) ^ ((uint64_t)rand()<<30) ^ ((uint64_t)rand()<<15) ^ rand())
#define RAND64() ((int64_t)(rand() & 1 ? URAND63() : -URAND63() - 1))

typedef struct _twoIntsStruct
{
	int intOne;
	int intTwo;
} twoIntsStruct;

#ifdef __cplusplus
extern "C" {
#endif

extern const int GLOBAL_CONST_TRUE;
extern const int GLOBAL_CONST_FALSE;
extern const int GLOBAL_CONST_FIVE;

extern int globalTrue;
extern int globalFalse;
extern int globalFive;

#ifdef __cplusplus
}
#endif

"""

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
	cmd = f"unifdef -DOMITGOOD -UOMITBAD -DINCLUDEMAIN -U_WIN32 {file_path}"
	result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
	if result.returncode != 0 and result.returncode != 1:
		print(f"Error processing {file_path}: {result.stderr}")
		return

	source_code = result.stdout
	
	if 'int main' not in source_code:
		print(f"Skipping {file_path} beacuse it doesn't have a main()")
		return

# 	# Remove specific function calls
# 	source_code = re.sub(r'\b(printLine|printStructLine|printIntLine|printLongLongLine|printHexCharLine|printWcharLine)\b\(.*?\);', '', source_code)
# 
# 	# Remove specific imports
# 	source_code = re.sub(r'#include\s+"std_testcase\.h"', '', source_code)

	# Remove comments
	cleaned_code = comment_remover(source_code)

	# Add stuff that was originally in a header file
	# cleaned_code = HEADER_REPLACEMENT + cleaned_code
	

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
			if file.endswith(('.c', '.cpp', '.h')) and file != "main.cpp":
				file_path = os.path.join(root, file)
				process_file(file_path, output_dir)

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print("Usage: python script.py <input_directory>")
		sys.exit(1)

	input_dir = sys.argv[1]
	output_dir = input_dir + '_processed'

	process_directory(input_dir, output_dir)

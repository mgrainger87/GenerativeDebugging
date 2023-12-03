import subprocess
import os
import sys

def git_diff_initial_final(repo_path, file_extensions):
	"""
	Get the diffs including the complete file for any file that was changed and the annotated diff showing changes.
	"""
	original_dir = os.getcwd()  # Save the original working directory
	output = ''
	try:
		os.chdir(repo_path)
	
		# Get the hash of the initial commit
		initial_commit = subprocess.check_output(["git", "rev-list", "--max-parents=0", "HEAD"], text=True).strip()
	
		# Get the hash of the final commit
		final_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
	
		# Get the list of changed files between the initial and final commit
		changed_files = subprocess.check_output(
			["git", "diff", "--name-only", initial_commit, final_commit] + [f'*.{ext}' for ext in file_extensions],
			text=True
		).splitlines()
	
		# Show the complete file and then the diff for each changed file
		for file in changed_files:
			file_contents = subprocess.check_output(["git", "show", f"{final_commit}:{file}"], text=True)
			file_diff = subprocess.check_output(["git", "diff", initial_commit, final_commit, file], text=True)
			output += f"--- {file} (Full File) ---\n{file_contents}\n"
			output += f"--- {file} (Diff) ---\n{file_diff}\n"
	
	except subprocess.CalledProcessError as e:
		output = f"Error processing repository at {repo_path}: {e}"
	finally:
		os.chdir(original_dir)  # Change back to the original directory
	
	return output


def is_diff_substantive(diff_output):
	"""
	Ask the user if the diff is substantive or not.
	"""
	print(diff_output)
	answer = input("Is the above diff substantive? (yes/no): ").strip().lower()
	return answer == 'yes'

def ask_user(question):
	"""
	Ask a yes/no question to the user and return True for 'yes' and False for 'no'.
	"""
	answer = input(question + " (yes/no): ").strip().lower()
	return answer == 'yes'
	
def process_repositories(base_directory, file_extensions):
	"""
	Process each subdirectory in the base directory as a separate git repository.
	"""
	diff_info = {}
	total_diffs = 0
	substantive_count = 0
	correct_count = 0
	
	for directory in os.listdir(base_directory):
		repo_path = os.path.join(base_directory, directory)
		if os.path.isdir(repo_path) and '.git' in os.listdir(repo_path) and 'succeeded.txt' in os.listdir(repo_path):
			print(f"Processing repository: {directory}")
			diff_output = git_diff_initial_final(repo_path, file_extensions)
			if diff_output:
				print(diff_output)
				total_diffs += 1
				is_substantive = ask_user("Is the above diff substantive?")
				is_correct = ask_user("Is the above diff correct?") if is_substantive else False
				diff_info[directory] = {'Substantive': is_substantive, 'Correct': is_correct}
				substantive_count += int(is_substantive)
				correct_count += int(is_correct)
	
	return diff_info, substantive_count, correct_count, total_diffs

# Directory containing the repositories (update this path)
base_directory = sys.argv[1]

# File extensions to include in the diff
file_extensions = ['c', 'cpp', 'h']

# Process the repositories
diff_info, substantive_count, correct_count, total_diffs = process_repositories(base_directory, file_extensions)

# Calculate percentages
substantive_percentage = (substantive_count / total_diffs) * 100 if total_diffs > 0 else 0
correct_percentage = (correct_count / substantive_count) * 100 if substantive_count > 0 else 0

# Display the results
print("\nDiff Information:", diff_info)
print(f"Total number of diffs: {total_diffs}")
print(f"Number of substantive diffs: {substantive_count}")
print(f"Substantive Percentage: {substantive_percentage:.2f}%")
print(f"Number of correct diffs: {correct_count}")
print(f"Correct Percentage (of substantive diffs): {correct_percentage:.2f}%")
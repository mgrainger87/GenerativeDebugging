import os
import shutil

def delete_empty_subdirs(source_dir, destination_dir):
	# Iterate through each subdirectory in the source directory
	for item in os.listdir(source_dir):
		source_subdir = os.path.join(source_dir, item)
		if os.path.isdir(source_subdir):
			dest_subdir = os.path.join(destination_dir, item)
			# Check if the corresponding directory exists in the destination and is empty
			if os.path.exists(dest_subdir) and not os.listdir(dest_subdir):
				# Delete the subdirectory from the source
				shutil.rmtree(source_subdir)
				# Delete the empty subdirectory from the destination
				shutil.rmtree(dest_subdir)
				print(f"Deleted source subdirectory: {item}")
				print(f"Deleted empty destination subdirectory: {item}")

	# Now check for any empty directories in the destination that are not in the source
	for item in os.listdir(destination_dir):
		dest_subdir = os.path.join(destination_dir, item)
		source_subdir = os.path.join(source_dir, item)
		if os.path.isdir(dest_subdir) and not os.path.exists(source_subdir) and not os.listdir(dest_subdir):
			# Delete the empty subdirectory from the destination
			shutil.rmtree(dest_subdir)
			print(f"Deleted empty destination subdirectory not present in source: {item}")

# Example usage
# delete_empty_subdirs('/path/to/source_dir', '/path/to/destination_dir')

delete_empty_subdirs('/Users/morgang/code/GenerativeDebugging/juliet', '/Users/morgang/code/GenerativeDebugging/results')

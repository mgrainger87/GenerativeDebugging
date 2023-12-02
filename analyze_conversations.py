import sys
import os
import pandas as pd
import json

def count_roles_and_functions(json_data):
	# Initialize a dictionary to keep the count of each role and function
	count = {"assistant": 0, "system": 0, "user": 0, "tool": 0, "functions": {}}

	# Iterate over each entry in the JSON data
	for entry in json_data:
		# Extract the role from the entry
		role = entry.get("role")

		# Increment the count for the role if it exists in the dictionary
		if role in count:
			count[role] += 1

		# If the entry is from the assistant and it contains tool calls, count the function names
		if role == "assistant" and "tool_calls" in entry:
			for tool_call in entry["tool_calls"]:
				function_name = tool_call["function"]["name"]
				count["functions"][function_name] = count["functions"].get(function_name, 0) + 1

	return count

def create_dataframe(directory_path):
	"""
	Recreate the DataFrame from the conversation.json files and add a column for the first part 
	of the last directory path segment.
	"""
	summary_data = []

	# Walk through the directory and its subdirectories
	for root, dirs, files in os.walk(directory_path):
		for file in files:
			if file == "conversation.json":
				file_path = os.path.join(root, file)

				with open(file_path, 'r') as json_file:
					data = json.load(json_file)
					counts = count_roles_and_functions(data)
					# Extract the first part of the last directory path segment
					directory_segment = root.split('/')[-1].split('_')[0]
					summary_data.append({"directory": root, "directory_segment": directory_segment, **counts})

	df = pd.DataFrame(summary_data)

	# Expand the function counts into separate columns and convert to integers
	functions_df = df['functions'].apply(pd.Series).fillna(0).astype(int)
	expanded_df = pd.concat([df.drop(columns=['functions']), functions_df], axis=1)

	return expanded_df

def expand_function_counts(df):
	"""
	Expand the function counts in the 'functions' column into separate columns in the DataFrame.
	"""
	# Extract function counts as a separate DataFrame
	functions_df = df['functions'].apply(pd.Series)

	# Combine the original DataFrame with the expanded functions DataFrame
	expanded_df = pd.concat([df.drop(columns=['functions']), functions_df], axis=1)

	return expanded_df

def add_directory_segment_column(df):
	"""
	Modify the DataFrame to include a column with the first part of the last directory path segment.
	For example, if the directory is '/path/to/CWE121_Some_Other_Text', 
	the new column will have the value 'CWE121'.
	"""
	# Extract the last segment of the directory path and then split it to get the first part
	df['directory_segment'] = df['directory'].apply(lambda x: x.split('/')[-1].split('_')[0])

	return df

def count_debugger_commands_extended(json_data):
	"""
	Count the number of different commands (first word) and subcommands (first two words) 
	issued by the run_debugger_command function.
	"""
	# Initialize dictionaries to keep the count of each command and subcommand
	command_counts = {}
	subcommand_counts = {}

	# Iterate over each entry in the JSON data
	for entry in json_data:
		# Check if the entry is from the assistant and it contains tool calls
		if entry.get("role") == "assistant" and "tool_calls" in entry:
			for tool_call in entry["tool_calls"]:
				if tool_call["function"]["name"] == "run_debugger_command":
					# Extract the command
					cmd = json.loads(tool_call["function"]["arguments"]).get("cmd", "")
					words = cmd.split()

					# Command name (first word)
					if words:
						command_name = words[0]
						command_counts[command_name] = command_counts.get(command_name, 0) + 1

					# Subcommand name (first two words)
					if len(words) > 1:
						subcommand_name = ' '.join(words[:2])
						subcommand_counts[subcommand_name] = subcommand_counts.get(subcommand_name, 0) + 1

	return command_counts, subcommand_counts

def count_all_debugger_commands(directory_path):
	# Initialize dictionaries to store the command and subcommand counts for all conversation.json files
	all_command_counts = {}
	all_subcommand_counts = {}
	
	# Walk through the directory and its subdirectories
	for root, dirs, files in os.walk(directory_path):
		for file in files:
			# Check if the file is conversation.json
			if file == "conversation.json":
				file_path = os.path.join(root, file)
	
				# Open and load the JSON file
				with open(file_path, 'r') as json_file:
					data = json.load(json_file)
	
					# Count the debugger commands and subcommands in the current file
					command_counts, subcommand_counts = count_debugger_commands_extended(data)
	
					# Update the overall command and subcommand counts
					for command, count in command_counts.items():
						all_command_counts[command] = all_command_counts.get(command, 0) + count
					for subcommand, count in subcommand_counts.items():
						all_subcommand_counts[subcommand] = all_subcommand_counts.get(subcommand, 0) + count
						
	return all_command_counts, all_subcommand_counts

def aggregate_conversations_by_segment(directory_path, segment):
	"""
	Aggregate the conversation.json files in the given directory and subdirectories,
	returning aggregated summary statistics in a DataFrame for the specified directory path segment.
	"""
	aggregated_data = {
		"directory_segment": segment,
		"assistant": 0,
		"system": 0,
		"user": 0,
		"tool": 0,
		"function_counts": {}
	}

	# Walk through the directory and its subdirectories
	for root, dirs, files in os.walk(directory_path):
		for file in files:
			if file == "conversation.json":
				# Check if the directory segment matches the specified segment
				directory_segment = root.split('/')[-1].split('_')[0]
				if directory_segment == segment:
					file_path = os.path.join(root, file)

					with open(file_path, 'r') as json_file:
						data = json.load(json_file)
						counts = count_roles_and_functions(data)
						
						# Aggregate the counts
						aggregated_data["assistant"] += counts["assistant"]
						aggregated_data["system"] += counts["system"]
						aggregated_data["user"] += counts["user"]
						aggregated_data["tool"] += counts["tool"]

						# Aggregate function counts
						for function, count in counts["functions"].items():
							aggregated_data["function_counts"][function] = (
								aggregated_data["function_counts"].get(function, 0) + count
							)

	# Create a DataFrame from the aggregated data
	function_counts_df = pd.Series(aggregated_data["function_counts"]).to_frame().T.fillna(0).astype(int)
	df = pd.DataFrame([{k: v for k, v in aggregated_data.items() if k != "function_counts"}])
	aggregated_df = pd.concat([df, function_counts_df], axis=1)

	return aggregated_df

def summarize_conversations_by_segment(df):
	if 'directory' in df.columns:
		df = df.drop(columns=['directory'])
	
	# Group by the directory segment and aggregate the counts
	aggregated_df = df.groupby('directory_segment').sum()
	
	# Add a 'count' column showing the number of test cases for each directory segment
	aggregated_df['count'] = df.groupby('directory_segment').size()
	
	return aggregated_df
	
def generate_latex_code_from_df(df):
	template = """
\\documentclass{{article}}
\\usepackage{{pgfplots}}
\\pgfplotsset{{compat=1.17}}

\\begin{{document}}

\\begin{{tikzpicture}}
\\begin{{axis}}[
	ybar stacked,
	bar width=15pt,
	width=8cm,
	height=7cm,
	enlargelimits=0.15,
	legend style={{
		at={{(0.5,-0.15)}},
		anchor=north,
		legend columns=2,
		column sep=0.5cm,
		legend cell align=left,
	}},
	ylabel={{Commands per Debugging Session}},
	ylabel near ticks,
	ymin=0,
	ymax=30,
	symbolic x coords={{{}}},
	xtick=data,
	xticklabel style={{rotate=0, anchor=north, align=center, text width=1.5cm,xshift=0pt}},
	]
{}
\\legend{{Run Debugger Command, Get Source, Modify Code, Restart, End Session}}
{}
\\end{{axis}}
\\end{{tikzpicture}}

\\end{{document}}
"""

	df_normalized = df[['run_debugger_command', 'get_source', 'modify_code', 'restart', 'end_session']].div(df['count'], axis=0)

	# Extract problem categories
	categories = ', '.join(df_normalized.index)
	
	# Prepare the data for each stack
	stacks = ["run_debugger_command", "get_source", "modify_code", "restart", "end_session"]
	stack_data = ""
	colors = ["blue!50", "red!50", "green!50", "orange!50", "gray!50"]
	
	for stack, color in zip(stacks, colors):
		stack_data += "\\addplot+[ybar, fill={}] plot coordinates {{".format(color)
		for category in df_normalized.index:
			stack_data += "({}, {}) ".format(category, df_normalized.at[category, stack])
		stack_data += "};\n"
		
	# Generate nodes for sums
	node_data = "\n"
	for category in df_normalized.index:
		sum_normalized = df_normalized.loc[category].sum()
		node_data += f"\\node at (axis cs:{category},{sum_normalized:.2f}) [above] {{{sum_normalized:.2f}}};\n"
	
	return template.format(categories, stack_data, node_data)

# Define the path to the directory containing the test data
directory_path = sys.argv[1]

# Recreate the DataFrame with directory segment
updated_df = create_dataframe(directory_path)
print("\nData frame:")
print(updated_df.head())  # Display the first few rows of the updated DataFrame for review

# Calculate the sum of each column in the DataFrame
print("\nNumber of conversation entries:")
print(updated_df.sum(numeric_only=True).to_dict())

print("\nBy segment:")
print(summarize_conversations_by_segment(updated_df))

print("\nAll debugger commands:")
print(count_all_debugger_commands(directory_path))

print("\nLaTeX code:")
latex_code = generate_latex_code_from_df(summarize_conversations_by_segment(updated_df))
print(latex_code)

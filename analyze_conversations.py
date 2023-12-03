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

# Function to create a DataFrame from a directory path
def create_dataframe(directory_path):
	summary_data = []
	for root, dirs, files in os.walk(directory_path):
		for file in files:
			if file == "conversation.json":
				file_path = os.path.join(root, file)
				with open(file_path, 'r') as json_file:
					data = json.load(json_file)
					counts = count_roles_and_functions(data)
					directory_segment = root.split('/')[-1].split('_')[0]
					# Check for success.txt file in the same directory
					success = 'succeeded.txt' in files
					summary_data.append({"directory": root, 
										 "directory_segment": directory_segment, 
										 "success": success, 
										 **counts})

	df = pd.DataFrame(summary_data)
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

					commands_without_subcommands = ["p", "print", "expr", "expression", "x/s", "disassemble"]
					if command_name in commands_without_subcommands:
						continue

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

% Secondary y-axis (line graph)
\\begin{{axis}}[
	width=8cm,
	height=7cm,
	enlargelimits=0.15,
	axis y line*=right,
	axis x line=none,
	symbolic x coords={{{}}},
	xtick=data,
	ylabel={{Success Rate (\%)}},
	ylabel near ticks,
	ymin=0,
	ymax=100,
	ytick={{0,20,...,100}},
	yticklabel=$\\pgfmathprintnumber{{\\tick}}$,
	nodes near coords={{
		\\pgfmathprintnumber[precision=0, fixed zerofill]{{\\pgfplotspointmeta}}
	}},
	every node near coord/.append style={{font=\\tiny}}
	]
\\addplot[sharp plot, mark=*] coordinates {{{}}};
\\end{{axis}}

\\end{{tikzpicture}}
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

	# Calculate success percentages
	success_percentages = calculate_success_percentage(df)

	# Prepare the data for the line graph
	line_graph_data = ""
	for category, percentage in success_percentages.items():
		line_graph_data += f"({category}, {percentage:.2f}) "

	return template.format(categories, stack_data, node_data, categories, line_graph_data)

# Generalized function with an exceptions list parameter to combine certain types of error messages
	
def count_errors_with_exceptions(directory, exceptions):
	error_count = {}
	prefix = "Command execution failed: error: "
	for root, dirs, files in os.walk(directory):
		if 'conversation.json' in files:
			with open(os.path.join(root, 'conversation.json'), 'r') as file:
				conversations = json.load(file)
				for conversation in conversations:
					content = conversation.get('content', '')
					if content:
						# Extract error string up to the first newline, strip the prefix and trailing period
						error_msg = content.split("\n")[0]
						if error_msg.startswith(prefix):
							stripped_error_msg = error_msg[len(prefix):].rstrip(".")

							# Check for exceptions and combine errors accordingly
							combined = False
							for exception, combined_key in exceptions.items():
								if exception in stripped_error_msg:
									combined_key_stripped = combined_key[len(prefix):].rstrip(".")
									error_count[combined_key_stripped] = error_count.get(combined_key_stripped, 0) + 1
									combined = True
									break
							
							# If not combined, count as a unique error
							if not combined:
								error_count[stripped_error_msg] = error_count.get(stripped_error_msg, 0) + 1

	# Sort the dictionary by count in descending order
	sorted_error_count = dict(sorted(error_count.items(), key=lambda item: item[1], reverse=True))
	return sorted_error_count

def calculate_success_percentage(df):
	# Initialize an empty dictionary to store the results
	success_percentages = {}
	
	# Iterate through each row in the DataFrame
	for index, row in df.iterrows():
		# Calculate success percentage
		success_percentage = (row['success'] / row['count']) * 100
	
		# Map the directory_segment to its success percentage
		success_percentages[index] = success_percentage
	
	return success_percentages

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
segment_df = summarize_conversations_by_segment(updated_df)
print(segment_df)

print("\nAll debugger commands:")
print(count_all_debugger_commands(directory_path))

print("\nLaTeX code:")
latex_code = generate_latex_code_from_df(segment_df)
print(latex_code)

print("\nSuccess percentages:")
print(calculate_success_percentage(segment_df))

# Define exceptions to combine specific types of error messages
exceptions = {
	"no variable named": "Command execution failed: error: no variable named",
	"memory read failed": "Command execution failed: error: memory read failed",
	"no modules found": "Command execution failed: error: no modules found",
	"unexpected char": "Command execution failed: error: unexpected char encountered",
	"invalid frame index argument": "Command execution failed: error: invalid frame index argument",
	"unexpected char": "Command execution failed: error: unexpected char encountered",
	"is not a valid command": "Command execution failed: not a valid command",
	"'memory read' will not read over 1024 bytes of data": "Command execution failed: error: 'memory read' will not read over 1024 bytes of data",
	"Couldn't apply expression side effects": "Command execution failed: error: Couldn't apply expression side effects",
	"Frame index (": "Command execution failed: error: Frame index out of range",
	"doesn't take any arguments": "Command execution failed: error: command doesn't take any arguments",
	"Invalid format character or name": "Command execution failed: error: Invalid format character or name",
	"address expression \"": "Command execution failed: error: address expression evaluation failed",
	"too many arguments": "Command execution failed: error: too many arguments",

}

# Count errors in the extracted folder with the generalized function and exceptions
print("\nError types and counts:")
generalized_error_counts = count_errors_with_exceptions(sys.argv[1], exceptions)
print(generalized_error_counts)

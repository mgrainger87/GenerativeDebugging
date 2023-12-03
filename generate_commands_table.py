
def escape_latex_special_chars(text):
	"""
	Escape LaTeX special characters in the given text.
	
	:param text: A string that might contain LaTeX special characters.
	:return: A string with LaTeX special characters escaped.
	"""
	# Define LaTeX special characters that need escaping
	special_chars = {
		'_': '\\textunderscore ',
		'$': '\\$',
		'&': '\\&',
		'%': '\\%',
		'#': '\\#',
		'{': '\\{',
		'}': '\\}',
		'~': '\\textasciitilde{}',
		'^': '\\textasciicircum{}',
		'\\': '\\textbackslash{}'
	}
	
	# Escape special characters
	for char, escaped_char in special_chars.items():
		if char != '\\':  # Handle backslash separately
			text = text.replace(char, escaped_char)
	
	# # Escape backslashes last to avoid double escaping
	# text = text.replace('\\', '\\textbackslash{}')
	
	return text


def create_latex_table_multi_count_escaped(main_cmds_list, sub_cmds_list):
	"""
	Generate a LaTeX table with escaped special characters from the provided list of dictionaries
	of main and sub commands, with multiple count columns.

	:param main_cmds_list: List of dictionaries of main commands and their counts.
	:param sub_cmds_list: List of dictionaries of sub-commands and their counts.
	:return: String representing the LaTeX table.
	"""
	# Combine all main and sub commands into a set for unified processing
	all_main_cmds = set()
	for cmds in main_cmds_list:
		all_main_cmds.update(cmds.keys())
	
	all_sub_cmds = set()
	for cmds in sub_cmds_list:
		all_sub_cmds.update(cmds.keys())

	# Start building the LaTeX table
	latex_table = "\\begin{table}\n\\centering\n\\caption{\\em LLDB Commands Requested During Debugging}\n" \
				  "\\label{tab:lldb_commands}\n\\begin{tabular}{p{0.6\\linewidth}"
	latex_table += "r" * len(main_cmds_list)  # Add columns for counts
	latex_table += "}\n\\toprule\nCommand"

	# Add headers for count columns
	for i in range(len(main_cmds_list)):
		latex_table += f"& Count {i + 1} "
	latex_table += "\\\\\n \\textit{(sub-instructions seen)} \\\\\n\\midrule\n"

	# Process each main command
	for cmd in sorted(all_main_cmds):
		# Add command name
		latex_table += f"\\textbf{{{escape_latex_special_chars(cmd)}}}"

		# Add counts for each main command from each dictionary
		for main_cmds in main_cmds_list:
			count = main_cmds.get(cmd, 0)
			latex_table += f" & \\textbf{{{count}}}"

		latex_table += " \\\\\n"

		# Process sub-commands related to the main command
		for sub_cmd in sorted(all_sub_cmds):
			if sub_cmd.startswith(f"{cmd} "):
				sub_cmd_formatted = escape_latex_special_chars(sub_cmd.replace(cmd, "").strip())

				# Add sub-command name
				latex_table += f"\\textit{{\\quad {sub_cmd_formatted}}}"

				# Add counts for each sub-command from each dictionary
				for sub_cmds in sub_cmds_list:
					sub_count = sub_cmds.get(sub_cmd, 0)
					latex_table += f" & \\textit{{{sub_count}}}"
				
				latex_table += " \\\\\n"

	latex_table += "\\bottomrule\n\\end{tabular}\n\\end{table}"

	return latex_table

def create_latex_table_ordered_by_sum(main_cmds_list, sub_cmds_list):
	"""
	Generate a LaTeX table with escaped special characters from the provided list of dictionaries
	of main and sub commands, ordered by the sum of their counts across columns. 
	Omit zero values.

	:param main_cmds_list: List of dictionaries of main commands and their counts.
	:param sub_cmds_list: List of dictionaries of sub-commands and their counts.
	:return: String representing the LaTeX table.
	"""
	
	# Calculate total sum of all main commands for each column
	total_sums = [sum(main_cmds.get(cmd, 0) for cmd in main_cmds) for main_cmds in main_cmds_list]
	
	# Combine and sum counts for all main and sub commands
	combined_main_cmds = {cmd: sum(d.get(cmd, 0) for d in main_cmds_list) for cmd in set().union(*main_cmds_list)}
	combined_sub_cmds = {cmd: sum(d.get(cmd, 0) for d in sub_cmds_list) for cmd in set().union(*sub_cmds_list)}

	# Sort main and sub commands by their combined counts
	sorted_main_cmds = sorted(combined_main_cmds.items(), key=lambda x: x[1], reverse=True)
	sorted_sub_cmds = sorted(combined_sub_cmds.items(), key=lambda x: x[1], reverse=True)

	# Start building the LaTeX table
	latex_table = "\\begin{table}\n\\centering\n\\caption{\\em LLDB Commands Requested During Debugging}\n" \
				  "\\label{tab:lldb_commands}\n\\begin{tabular}{p{0.6\\linewidth}"
	latex_table += "r" * len(main_cmds_list)  # Add columns for counts
	latex_table += "}\n\\toprule\nCommand"

	# Add headers for count columns
	for i in range(len(main_cmds_list)):
		latex_table += f"& Count {i + 1} "
	latex_table += "\\\\\n \\textit{(sub-commands seen)} \\\\\n\\midrule\n"

	# Process each main command
	for cmd, _ in sorted_main_cmds:
		# Add command name
		latex_table += f"\\textbf{{{escape_latex_special_chars(cmd)}}}"

		# Add counts for each main command from each dictionary
		for main_cmds in main_cmds_list:
			count = main_cmds.get(cmd, 0)
			count_text = f"\\textbf{{{count}}}" if count != 0 else "--"
			latex_table += f" & {count_text}"

		latex_table += " \\\\\n"

		# Process and sort sub-commands related to the main command
		related_sub_cmds = [(sub_cmd, sub_count) for sub_cmd, sub_count in sorted_sub_cmds if sub_cmd.startswith(f"{cmd} ")]
		for sub_cmd, _ in related_sub_cmds:
			sub_cmd_formatted = escape_latex_special_chars(sub_cmd.replace(cmd, "").strip())

			# Add sub-command name
			latex_table += f"\\textit{{\\quad {sub_cmd_formatted}}}"

			# Add counts for each sub-command from each dictionary
			for sub_cmds in sub_cmds_list:
				sub_count = sub_cmds.get(sub_cmd, 0)
				sub_count_text = f"\\textit{{{sub_count}}}" if sub_count != 0 else "--"
				latex_table += f" & {sub_count_text}"
			
			latex_table += " \\\\\n"

	# Add total sum row for main commands
	latex_table += "\\midrule\n\\textbf{Total} "
	for total in total_sums:
		latex_table += f"& \\textbf{{{total}}} "
	latex_table += "\\\\\n"

	latex_table += "\\bottomrule\n\\end{tabular}\n\\end{table}"

	return latex_table

# Updated data
main_commands_list = [
	{'frame': 839, 'expr': 25, 'break': 2, 'run': 3, 'breakpoint': 2, 'thread': 23, 'log': 3, 'print': 10, 
	 'continue': 18, 'bt': 36, 'register': 6, 'memory': 87, 'r': 1, 'p': 13, 'up': 1, 'list': 1, 
	 'disassemble': 5, 'process': 15, 'expression': 4, 'settings': 2, 
	 'imaginary_command_to_check_memory_allocation': 1, 'image': 8, 'restart': 3, 'info': 2, 'x/s': 8, 'fr': 1, 
	 'next': 1, 'backtrace': 1, 'target': 1},
	{'frame': 200, 'memory': 3, 'breakpoint': 4, 'process': 3, 'bt': 2, 'continue': 1},
]

sub_commands_list = [
	{'frame variable': 535, 'frame select': 301, 'break set': 2, 'breakpoint set': 2, 'thread list': 12, 
	 'thread backtrace': 8, 'log show': 3, 'thread select': 1, 'register read': 6, 'memory read': 84, 
	 'frame info': 3, 'thread step-in': 1, 'process continue': 1, 'settings set': 1, 'settings show': 1, 
	 'image lookup': 2, 'memory info': 3, 'process launch': 7, 'image list': 6, 'info frame': 2, 'thread info': 1, 
	 'fr v': 1, 'process save-core': 2, 'process kill': 5, 'target modules': 1},
	{'frame select': 124, 'frame variable': 76, 'memory history': 1, 'breakpoint set': 4, 'process continue': 3, 'memory read': 2},
]

# Generate LaTeX table with the updated data, commands and sub-commands ordered by the sum of their counts
latex_output_updated_data = create_latex_table_ordered_by_sum(main_commands_list, sub_commands_list)
print(latex_output_updated_data)

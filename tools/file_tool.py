from langchain.tools import tool



MAX_LLM_BUFFER = 30000  # Example size, adjust as needed

class FileTool:
    @staticmethod
    @tool("""File Management Tool""")
    def manage_file(file_name: str, action: str = 'read', line_number: int = None, expected_text: str = None, new_text: str = None, create_if_missing: bool = False, append_text: str = None):
        """
        Manages various file operations such as reading, appending, editing, creating, counting lines, and retrieving specific lines.

        Parameters:
        - file_name (str): The path to the file to be managed. This is mandatory for all operations.
        - action (str): The operation to perform on the file. Supported actions include 'append', 'edit', 'create', 'count_lines', 'get_line', 'read'. For 'read', line_number specifies the starting line to read from.
        - line_number (int, optional): Specifies the line number for 'edit', 'get_line', or the line for 'read' to start at. It is a 1-based index.
        - expected_text (str, optional): For the 'edit' action, this is the text expected to be on the specified line. The line will only be edited if the text matches.
        - new_text (str, optional): For the 'edit' action, this is the new text that will replace the existing text on the specified line.
        - create_if_missing (bool, optional): For the 'create' action, if true, creates the file if it does not exist. This parameter is ignored for other actions.
        - append_text (str, optional): For the 'append' action, this is the text to be appended to the file.

        Returns:
        A string describing the outcome of the operation. Possible responses include:
        - The file's contents with line numbers for the 'read' action.
        - A success message for 'append', 'create', 'edit', 'count_lines', and 'get_line' actions.
        - A message indicating the file is empty or contains no readable characters if applicable.
        - Error messages for invalid parameters or if the specified actions cannot be completed.

        Raises:
        - ValueError: If the 'action' parameter is invalid or required parameters for an action are missing.
        - FileNotFoundError: If the 'file_name' does not exist for actions other than 'create' with create_if_missing=True, or if the specified line number is not found for 'edit' and 'get_line' actions.
        
        The tool only supports utf-8 encoding.
        
        """
        action_methods = {
            'append': FileTool._append_text,
            'edit': FileTool._edit_line,
            'create': FileTool._create_file,
            'count_lines': FileTool._count_lines,
            'get_line': FileTool._get_line,
            'read': FileTool._read_file
        }

        if action not in action_methods:
            valid_actions = ', '.join(action_methods.keys())
            raise ValueError(f"Invalid action '{action}' specified. Valid actions are: {valid_actions}.")

        # Adjusting the call to potentially include line_number for the 'read' action
        if action == 'read' and line_number is not None:
            return action_methods[action](file_name=file_name, start_line=line_number)
        else:
            # For all other actions, invoke the appropriate method using **locals() to pass named arguments
            return action_methods[action](**locals())
    
    @staticmethod
    def _append_text(file_name, append_text=None, **kwargs):
        """Appends text to the end of the specified file."""
        if append_text is None:
            return "No text provided to append."
        try:
            with open(file_name, 'a') as file:
                file.write(append_text + '\n')
            return "Text appended successfully."
        except FileNotFoundError:
            return f"File '{file_name}' not found."
    
    @staticmethod
    def _edit_line(file_name, line_number, expected_text, new_text, **kwargs):
        """Edits a specific line in the file if the expected text matches."""
        # Read the file's current content
        lines = FileTool._read_file_lines(file_name)
        if not 1 <= line_number <= len(lines):
            return f"Error: Line number {line_number} is out of the file's range."
        # Check if the expected text matches the current line content
        current_line = lines[line_number - 1].rstrip("\n")
        if current_line != expected_text:
            return f"Error: Expected text does not match the text on line {line_number}."
        # Replace the line with new text
        lines[line_number - 1] = new_text + '\n'
        # Write the updated lines back to the file
        FileTool._write_file_lines(file_name, lines)
        return "Line edited successfully."


    @staticmethod
    def _read_file(file_name, start_line=1, **kwargs):
        """Reads and returns the content of the specified file from a specified line, in manageable parts if necessary."""
        lines = FileTool._read_file_lines(file_name)[start_line-1:]  # Adjust to read from the specific line
        content = ''.join([f"{idx + start_line}: {line}" for idx, line in enumerate(lines)])
        if len(content) > MAX_LLM_BUFFER:
            cut_off_index = content[:MAX_LLM_BUFFER].rfind('\n')
            first_part = content[:cut_off_index]
            next_line_number = start_line + content.count('\n', 0, cut_off_index)
            remaining_content_indicator = (f"\n\n-- TOOL MESSAGE: Attention! Not all of the lines of the file have been read! --\n"
                f"ACTION REQUIRED: To continue reading the next part of the file, please issue a command using 'read' followed by the parameter 'line_number' set to the value specified below.\n"
                f"Next 'line_number': {next_line_number}\n")
        

            return first_part + remaining_content_indicator
        return content

    @staticmethod
    def _create_file(file_name, create_if_missing, **kwargs):
        """Creates a new file if it does not exist."""
        if create_if_missing:
            try:
                with open(file_name, 'x') as file:
                    return "File created successfully."
            except FileExistsError:
                return "File already exists."
        return "Creation flag not set; file not created."
    
    @staticmethod
    def _count_lines(file_name, **kwargs):
        """Counts the number of lines in the specified file."""
        lines = FileTool._read_file_lines(file_name)
        return f"Total lines: {len(lines)}"

    @staticmethod
    def _get_line(file_name, line_number, **kwargs):
        """Retrieves and returns a specific line from the specified file."""
        lines = FileTool._read_file_lines(file_name)
        if line_number < 1 or line_number > len(lines):
            return "Line number is out of range."
        return lines[line_number - 1].strip()
    
    @staticmethod
    def _read_file_lines(file_name):
        """Reads all lines from the specified file and returns them as a list."""
        with open(file_name, 'r') as file:
            return file.readlines()
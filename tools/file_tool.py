from langchain.tools import tool
import fileinput
import sys
import re

class FileTool:
    @tool("""File Management Tool""")
    def manage_file(file_name: str, line_number: int = None, expected_text: str = None, new_text: str = None, create_if_missing: bool = False, append_text: str = None):
        """
        Manages a file by either editing a specific line, appending text to it, creating the file
        if it does not exist, or reading its content. Depending on the parameters provided, it can perform
        one of these actions. This function can also check if a file is empty or contains no readable characters
        and return an appropriate message. When editing a line, it now also displays the previous and next lines 
        (with their line numbers) along with the success message, if those lines exist.

        :param file_name: Path to the file to be managed.
        :param line_number: The line number to edit (1-based index). If None, the file will be read instead.
                            For replacing text, line_number and expected_text are mandatory.
        :param expected_text: The expected text at the specified line. Required if line_number is provided.
        :param new_text: The new text to replace the original. Required if line_number and expected_text are provided.
        :param create_if_missing: If True, creates the file if it does not exist. This is only valid when not editing.
        :param append_text: The text to append to the file. If provided, the method will append this text to the file.
        :raises ValueError: If the expected text does not match the actual text at the specified line.
        :raises FileNotFoundError: If the specified file does not exist and create_if_missing is False, or if the specified line number is not found.
        :return: A string containing:
                - The file contents with line numbers when reading,
                - A success/failure message for append, create, or edit actions,
                - A message stating the file is empty or contains no readable characters if applicable.
        """
        response = ""
        if append_text is not None:
            # Append mode
            try:
                with open(file_name, 'a') as file:
                    file.write(append_text + '\n')
                response = "Text appended successfully."
            except Exception as e:
                response = f"Unexpected error appending to file '{file_name}': {e}"
        elif line_number is not None and expected_text is not None and new_text is not None:
            # Edit mode
            try:
                line_edited = False
                temp_lines = []
                with open(file_name, 'r') as file:
                    temp_lines = file.readlines()
                    if not temp_lines:  # Check if file is empty
                        return f"File '{file_name}' is empty or contains no readable characters."
                with open(file_name, 'w') as file:
                    for i, line in enumerate(temp_lines, start=1):
                        if i == line_number:
                            if re.search(rf'^\s*{re.escape(expected_text)}\s*$', line):
                                file.write(new_text + '\n')
                                line_edited = True
                                prev_line = f"{line_number-1}: {temp_lines[i-2]}" if i > 1 else ""
                                next_line = f"{line_number+1}: {temp_lines[i]}" if i < len(temp_lines) else ""
                                response = f"Line {line_number} successfully edited.\n{prev_line}{next_line}"
                            else:
                                raise ValueError(f"Expected text '{expected_text}' does not match actual text at line {line_number}.")
                        else:
                            file.write(line)
                if not line_edited:
                    raise FileNotFoundError(f"Line number {line_number} not found in file '{file_name}'.")
            except FileNotFoundError as fnfe:
                response = f"{fnfe}"
            except ValueError as ve:
                response = f"{ve}"
            except Exception as e:
                response = f"Unexpected error editing file '{file_name}': {e}"
        elif create_if_missing:
            # Create file if missing
            try:
                with open(file_name, 'x') as file:
                    response = f"File '{file_name}' created successfully."
            except FileExistsError:
                response = f"File '{file_name}' already exists."
            except Exception as e:
                response = f"Unexpected error creating file '{file_name}': {e}"
        else:
            # Read mode
            try:
                file_contents = []
                with open(file_name, 'r') as file:
                    for i, line in enumerate(file, start=1):
                        file_contents.append(f"{i}: {line}")
                if not file_contents:  # Check if file is empty
                    response = f"File '{file_name}' is empty or contains no readable characters."
                else:
                    response = "".join(file_contents)
            except FileNotFoundError as fnfe:
                response = f"File '{file_name}' not found: {fnfe}"
            except Exception as e:
                response = f"Unexpected error reading file '{file_name}': {e}"
        
        return response

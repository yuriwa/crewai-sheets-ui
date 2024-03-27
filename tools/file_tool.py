from langchain.tools import tool
import fileinput
import sys
import re

class FileTool:
    @tool("""File Management Tool""")
    def manage_file(file_name: str, line_number: int = None, expected_text: str = None, new_text: str = None, create_if_missing: bool = False, append_text: str = None):
        """
        Manages a file by either editing a specific line, reading the file with line numbers, creating the file
        if it does not exist, or appending text to it, based on the parameters provided.

        :param file_name: Path to the file to be managed.
        :param line_number: The line number to edit (1-based index). If None, the file will be read instead. For replaceing text line_number is mandatory.
        :param expected_text: The expected text at the specified line. Required if line_number is provided.
        :param new_text: The new text to replace the original. Required if line_number is provided.
        :param create_if_missing: If True, creates the file if it does not exist. Only valid when not editing.
        :param append_text: The text to append to the file. If provided, the method will append this text to the file.
        :raises ValueError: If the expected text does not match the actual text at the specified line.
        :raises FileNotFoundError: If the specified file does not exist and create_if_missing is False.
        :return: A string containing the file contents with line numbers when reading, a success/failure message otherwise, or a confirmation message after appending text.
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
                with fileinput.input(files=file_name, inplace=True, backup='.bak') as file:
                    for i, line in enumerate(file, start=1):
                        if i == line_number:
                            if re.search(rf'^\s*{re.escape(expected_text)}\s*$', line):
                                print(new_text, end='\n')
                                line_edited = True
                                response = f"Line {line_number} successfully edited."
                            else:
                                raise ValueError(f"Expected text '{expected_text}' does not match actual text at line {line_number}.")
                        else:
                            print(line, end='')
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
                response = "".join(file_contents)
                print("The contents of the file is in the response")
            except FileNotFoundError as fnfe:
                response = f"File '{file_name}' not found: {fnfe}"
            except Exception as e:
                response = f"Unexpected error reading file '{file_name}': {e}"
        
        return response
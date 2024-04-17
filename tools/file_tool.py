import logging
from langchain.tools import tool
from typing import Optional, Type, Any
from pydantic.v1 import BaseModel, Field, validator
from crewai_tools import BaseTool
from enum import Enum
logging.basicConfig(level=logging.INFO)
# Get the logger for the current file, respecting the configuration from main.py
logger = logging.getLogger(__name__)


class FixedFileToolSchema(BaseModel):
    """Input for FileTool."""
    pass

class FileToolSchema(FixedFileToolSchema):
    """Input for FileTool."""
    file_path: str = Field(..., description="The path to the file.")
    action: str = Field(..., description="The action to perform on the file.")
    line_number: int = Field(None, description="The line number to start reading from. Line numbers are 1-based.")
    num_lines: Optional[int] = Field(None, description="The number of lines to read starting from line_number.")
    expected_text: str = Field(None, description="The text expected to be on the specified line for editing.")
    new_text: str = Field(None, description="The new text to replace the existing text on the specified line.")
    append_text: str = Field(None, description="The text to be appended to the file.")

    # @validator('file_path')
    # def check_file_exists(cls, v, values):
    #     import os
    #     if values['action'] != ActionType.create and not os.path.exists(v):
    #         raise ValueError("file must exist for the specified action")
    #     return v

    # @validator('line_number', 'expected_text', 'new_text', 'append_text', always=True)
    # def check_required_fields(cls, v, values):
    #     action = values.get('action')
    #     if action == ActionType.edit and v is None:
    #         raise ValueError("'Line_number', 'expceted_text' and 'new_text' is required for the 'edit' action")
    #     if action == ActionType.append and v is None:
    #         raise ValueError("'append_text' is required for 'append' action")
    #     if action == ActionType.get_line and v is None:
    #         raise ValueError("'line_number' is required for 'get_line' action")
    #     return v

class FileTool(BaseTool):
    name: str = "General purpose file management tool"
    description: str = "Manage append, edit, create, count_lines, read a line, read from line onwards, read, create file operations"
    args_schema: Type[BaseModel] = FileToolSchema
    file_path: Optional[str] = None
    
    def __init__(self, file_path: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.description = """
Supported Actions:
    - Append: Adds specified text to the end of the file.
      Parameters:
        - file_path: Path to the file.
        - append_text: Text to be appended.

    - Edit: Modifies a specific line in the file, provided the existing content matches the expected input.
      Parameters:
        - file_path: Path to the file.
        - line_number: Line number to edit.
        - expected_text: The text currently expected on the line.
        - new_text: The new text to replace the existing line content.

    - Create: Generates a new file or overwrites an existing file.
      Parameters:
        - file_path: Path to the file where the new file will be created.

    - Count Lines: Calculates the total number of lines in the file.
      Parameters:
        - file_path: Path to the file.

    - Get Line: Retrieves the content of a specific line based on line number.
      Parameters:
        - file_path: Path to the file.
        - line_number: The line number whose content is to be retrieved.

    - Read: Extracts a segment of the file starting from a specified line and covering a defined number of subsequent lines.
      Parameters:
        - file_path: Path to the file.
        - line_number: The starting line number from where to begin reading.
        - num_lines: The number of lines to read from the starting line. If not specified, reads all lines starting from `line_number`.
    Line numbers are 1-based, meaning the first line is line 1.
    """
        if file_path is not None:
            self.file_path = file_path
        else:
            self._generate_description
        

    def _run(self, **kwargs: Any) -> Any:
        try:
            self.args_schema = FixedFileToolSchema
            action = kwargs.get('action', '').lower()  # Convert action to lowercase, default to empty string if None
            if action == 'append':
                return self._append_text(**kwargs)
            elif action == 'edit':
                return self._edit_line(**kwargs)
            elif action == 'create':
                return self._create_file(**kwargs)
            elif action == 'count_lines':
                return self._count_lines(**kwargs)
            elif action == 'get_line':
                return self._get_line(**kwargs)
            elif action == 'read':
                return self._read_file(**kwargs)
            else:
                self.description = f"Invalid action '{action}'. Valid actions are: append, edit, create, count_lines, get_line, read."
                self._generate_description()
                return self.description
        except Exception as e:
            error_message = f"Error processing action '{kwargs.get('action', 'unknown')}'. Exception type: {type(e).__name__}, Exception info: {e}, Object state: {self.__dict__}"
            # Optionally log or handle the error message further
            return error_message
        	
        
    def _append_text(self, file_path, append_text=None, **kwargs):
        try:
            with open(file_path, 'a') as file:
                file.write(append_text + '\n')
            return "Text appended successfully."
        except Exception as e:
            return f"Failed to append text: {e}"

    def _edit_line(self, file_path, line_number, expected_text, new_text, **kwargs):
        """Edits a specific line in the file if the expected text matches."""
        lines = self._read_file_lines(file_path)
        if not 1 <= line_number <= len(lines):
            return f"Error: Line number {line_number} is out of the file's range. The file has {len(lines)} lines. The first line is line 1."
        # Check if the expected text matches the current line content
        current_line = lines[line_number - 1].rstrip("\n")
        if expected_text is not None and current_line != expected_text:
            return f"Error: Expected text does not match the text on line {line_number}."
        # Replace the line with new text
        lines[line_number - 1] = new_text + '\n'
        # Write the updated lines back to the file directly within this method
        with open(file_path, 'w') as file:
            file.writelines(lines)
        return "Line edited successfully."
    
    def _read_file(self, file_path, line_number=1, num_lines=None, **kwargs):
        """Reads a specific number of lines starting from a given line number."""
        if line_number is None:
            logger.error("Line number is None, defaulting to 1")
            line_number = 1  # Default to the first line if none is specified.

        lines = self._read_file_lines(file_path)
        
        # Validate line_number to ensure it's within the range of the file's line count.
        if line_number < 1 or line_number > len(lines):
            return f"Error: Line number {line_number} is out of the file's range."

        # Calculate the end index for slicing lines; handle case where num_lines is None
        end_index = (line_number - 1) + num_lines if num_lines is not None else None
        selected_lines = lines[line_number - 1:end_index]  # Adjust for zero-based index

        if not selected_lines:
            return "No lines found starting from the specified line number."

        content = ''.join([f"{idx + line_number}: {line}" for idx, line in enumerate(selected_lines)])
        return content

    def _create_file(self, file_path, **kwargs):
        """Creates a new file or overwrites an existing one."""
        try:
            with open(file_path, 'x') as file:
                return "File created successfully."
        except FileExistsError:
            return "File already exists."

    def _count_lines(self, file_path, **kwargs):
        """Counts the number of lines in the specified file."""
        lines = self._read_file_lines(file_path)
        return f"Total lines: {len(lines)}"

    def _get_line(self, file_path, line_number, **kwargs):
        """Retrieves and returns a specific line from the specified file."""
        lines = self._read_file_lines(file_path)
        if line_number < 1 or line_number > len(lines):
            return "Line number is out of range."
        return lines[line_number - 1].strip()

    def _read_file_lines(self, file_path):
        """Reads all lines from the specified file and returns them as a list."""
        with open(file_path, 'r') as file:
            return file.readlines()
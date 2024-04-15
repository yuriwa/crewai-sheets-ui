import logging
from langchain.tools import tool
from typing import Optional, Type, Any
from pydantic.v1 import BaseModel, Field, validator
from crewai_tools import BaseTool
from enum import Enum
logging.basicConfig(level=logging.INFO)
# Get the logger for the current file, respecting the configuration from main.py
logger = logging.getLogger(__name__)


class ActionType(Enum):
    read = 'read'
    append = 'append'
    edit = 'edit'
    create = 'create'
    count_lines = 'count_lines'
    get_line = 'get_line'

class FixedFileToolSchema(BaseModel):
    """Input for FileTool."""
    pass

class FileToolSchema(FixedFileToolSchema):
    """Input for FileTool."""
    file_path: str = Field(..., description="The path to the file.")
    action: ActionType = Field(..., description="The action to perform on the file.")
    line_number: int = Field(None, description="The line number for actions that require one.")
    expected_text: str = Field(None, description="The text expected to be on the specified line for editing.")
    new_text: str = Field(None, description="The new text to replace the existing text on the specified line.")
    append_text: str = Field(None, description="The text to be appended to the file.")

    @validator('file_path')
    def check_file_exists(cls, v, values):
        import os
        if values['action'] != ActionType.create and not os.path.exists(v):
            raise ValueError("file must exist for the specified action")
        return v

    @validator('line_number', 'expected_text', 'new_text', 'append_text', always=True)
    def check_required_fields(cls, v, values):
        action = values.get('action')
        if action == ActionType.edit and v is None:
            raise ValueError("'Line_number', 'expceted_text' and 'new_text' is required for the 'edit' action")
        if action == ActionType.append and v is None:
            raise ValueError("'append_text' is required for 'append' action")
        if action == ActionType.get_line and v is None:
            raise ValueError("'line_number' is required for 'get_line' action")
        return v

class FileTool(BaseTool):
    name: str = "General purpose file management tool"
    description: str = "Manage append, edit, create, count_lines, read a line, read from line onwards, read, create file operations"
    args_schema: Type[BaseModel] = FileToolSchema
    file_path: Optional[str] = None
    
    def __init__(self, file_path: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        if file_path is not None:
            self.file_path = file_path
            self.description = f"A tool that can be used to manage append, edit, create, count_lines, read a line, read from line onwards, read {file_path}'s operations "
        else:
            self.description = f"A tool that can be used to manage append, edit, create, count_lines, read a line, read from line onwards, read, create a file. Takes arguments: file_path, action, line_number, expected_text, new_text, append_text"

			
        self.args_schema = FixedFileToolSchema
        self._generate_description()
                
        
    def _run(self, **kwargs: Any) -> Any:
        action      = kwargs.get('action')
        file_path   = kwargs.get('file_path', self.file_path)
        line_number = kwargs.get('line_number')
        expected_text= kwargs.get('expected_text')
        new_text     = kwargs.get('new_text')
        append_text  = kwargs.get('append_text')
        self.action_methods = {
            ActionType.append       : self._append_text,
            ActionType.edit         : self._edit_line,
            ActionType.create       : self._create_file,
            ActionType.count_lines  : self._count_lines,
            ActionType.get_line     : self._get_line,
            ActionType.read         : self._read_file
        }

        if action not in self.action_methods:
            logger.error(f"Invalid action '{action}'. Valid actions are: {list(self.action_methods.keys())}.")
            raise ValueError(f"Invalid action '{action}'. Valid actions are: {list(self.action_methods.keys())}.")

        # Perform the action
        logger.info(f"Performing action {action} on file {file_path}")
        return self.action_methods[action](file_path, line_number=line_number, expected_text=expected_text, new_text=new_text, append_text=append_text)

    def _append_text(self, file_path, append_text=None, **kwargs):
        try:
            with open(file_path, 'a') as file:
                file.write(append_text + '\n')
            logger.info("Text appended successfully.")
            return "Text appended successfully."
        except Exception as e:
            logger.error(f"Failed to append text: {e}")
            return f"Failed to append text: {e}"

    def _edit_line(self, file_path, line_number, expected_text, new_text, **kwargs):
        """Edits a specific line in the file if the expected text matches."""
        lines = self._read_file_lines(file_path)
        if not 1 <= line_number <= len(lines):
            return f"Error: Line number {line_number} is out of the file's range."
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

    def _read_file(self, file_path, start_line=1, **kwargs):
        lines = self._read_file_lines(file_path)[start_line - 1:]
        content = ''.join([f"{idx + start_line}: {line}" for idx, line in enumerate(lines)])
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
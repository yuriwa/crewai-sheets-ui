from langchain.tools import tool
from interpreter import interpreter

from langchain_openai import ChatOpenAI
interpreter.auto_run = True
#interpreter.offline = True # Disables online features like Open Procedures
#interpreter.llm.model = "openai/x" # Tells OI to send messages in OpenAI's format
#interpreter.llm.api_key = "fake_key" # LiteLLM, which we use to talk to LM Studio, requires this
#interpreter.llm.api_base = "http://localhost:1234/v1" # Point this at any OpenAI compatible server
interpreter.llm.context_window = 32768 #TODO remove hardcoding
interpreter.llm.model = "openai/gpt-4-turbo-preview"#Todo remove hardcoding

class CLITool:
    @tool("Executor")
    def execute_cli_command(command: str):
        """Create and Execute code using Open Interpreter."""
        interpreter.anonymized_telemetry = False
        result = interpreter.chat(command)
        return result


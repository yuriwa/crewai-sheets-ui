from rich.markdown import Markdown
from rich.console import Console
from rich.table import Table
import logging
import os
from dotenv import load_dotenv
from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI, AzureOpenAI, AzureChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
from ollama import pull, list
from utils import ollama_mod_and_load
import numpy as np

# ASCII art and greetings print functions
def greetings_print():
    console = Console()
    console = Console(force_terminal=True, force_interactive=True)
    # ASCII art
    ascii_art = """
 ██████ ██████  ███████ ██     ██      █████  ██      ██████  ██    ██ ██ 
██      ██   ██ ██      ██     ██     ██   ██ ██     ██       ██    ██ ██ 
██      ██████  █████   ██  █  ██     ███████ ██     ██   ███ ██    ██ ██ 
██      ██   ██ ██      ██ ███ ██     ██   ██ ██     ██    ██ ██    ██ ██ 
 ██████ ██   ██ ███████  ███ ███      ██   ██ ██      ██████   ██████  ██ 
                                                                                                                                                    
"""
    console.print(ascii_art)
    # Create a markdown string for the greeting message
    greeting_message = """
# How to use this app

Copy this sheet template and create your agents and tasks:
[https://docs.google.com/spreadsheets/d/1a5MBMwL9YQ7VXAQMtZqZQSl7TimwHNDgMaQ2l8xDXPE](https://docs.google.com/spreadsheets/d/1a5MBMwL9YQ7VXAQMtZqZQSl7TimwHNDgMaQ2l8xDXPE)
"""
    # Print the greeting using Rich's Markdown support for nice formatting
    console.print(Markdown(greeting_message))
    console.print("\n")


def after_read_sheet_print(agents_df, tasks_df):
    console = Console()
    terminal_width = console.width  # Get the current width of the terminal

    # Ensure the terminal width is at least 120 characters
    terminal_width = max(terminal_width, 120)

    # Calculate column widths based on terminal width
    # Adjust these ratios as needed to better fit your data
    agent_role_width = max(int(terminal_width * 0.1), 10)  # 20% of terminal width, at least 20 characters
    goal_width = max(int(terminal_width * 0.3), 30)        # 40% of terminal width, at least 40 characters
    backstory_width = max(int(terminal_width * 0.6), 60)   # 40% of terminal width, at least 40 characters

    task_name_width = max(int(terminal_width * 0.1),10)   # 20% of terminal width, at least 20 characters
    agent_width = max(int(terminal_width * 0.2), 20)       # 20% of terminal width, at least 20 characters
    instructions_width = max(int(terminal_width * 0.7), 70) # 60% of terminal width, at least 60 characters

    # Create a table for agents
    agents_table = Table(show_header=True, header_style="bold magenta")
    agents_table.add_column("Agent Role", style="dim", width=agent_role_width)
    agents_table.add_column("Goal", width=goal_width)
    agents_table.add_column("Backstory", width=backstory_width)

    # Add rows to the agents table
    for index, row in agents_df.iterrows():
        agents_table.add_row()
        agents_table.add_row(row['Agent Role'], row['Goal'], row['Backstory'])


    # Create a table for tasks
    tasks_table = Table(show_header=True, header_style="bold magenta")
    tasks_table.add_column("Task Name", style="dim", width=task_name_width)
    tasks_table.add_column("Agent", width=agent_width)
    tasks_table.add_column("Instructions", width=instructions_width)

    # Add rows to the tasks table
    for index, row in tasks_df.iterrows():
        tasks_table.add_row()
        tasks_table.add_row(row['Task Name'], row['Agent'], row['Instructions'])

    console.print("\nFound following agents and tasks in the google sheet:")
    # Display the tables
    console.print(agents_table)
    console.print(tasks_table)

# Helper function to convert strings to boolean
def str_to_bool(value_str):
    if isinstance(value_str, (bool, np.bool_)):
        return value_str
    else:
        return value_str.lower() in ['true', '1', 't', 'y', 'yes']

# Function to load environment variables
def load_env(env_path, expected_vars=None):
    """
    Load environment variables from a .env file and verify expected variables with stylized print output.
    
    :param env_path: Path to the .env file, can be relative or absolute.
    :param expected_vars: A list of environment variable names that are expected to be set.
    """
    # Convert to absolute path if necessary
    if not os.path.isabs(env_path):
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), env_path)
    
    loaded = load_dotenv(env_path)
    if not loaded:
        print(f"\033[93mWarning: Failed to load the .env file from '{env_path}'. Environment variables may not be set.\033[0m")
        return

    if expected_vars:
        missing_vars = [var for var in expected_vars if not os.getenv(var)]
        if missing_vars:
            print(f"\033[93mWarning: Missing expected environment variables: {', '.join(missing_vars)}\033[0m")

# Enhanced get_llm function with checking provider and model pulling in Ollama
def get_llm( model_name = None, 
            temperature = 0.7, 
            num_ctx     = None, 
            provider    = None, 
            base_url    = None, 
            deployment  = None,
            progress    = None, 
            llm_task    = None ):
    """
    Returns the appropriate LLM based on the model name and temperature.
    Checks if the specific model or base model already exists in Ollama and does not attempt to pull if it does,
    otherwise, it attempts to pull the model.

    :param model_name: The name of the model to load, potentially including a version.
    :param temperature: The temperature setting for the model.
    :return: An instance of the LLM.
    """

    # Define OpenAI models for direct use with the OpenAI API
    # openai_models = ["gpt-3.5-turbo", "gpt-4-turbo-preview"]        #TODO: Take this list from sheet
    #azure_models=["gpt4-azure", "gpt-4-1106-azure", "gpt-35-turbo-instruct"]                                       #TODO: Take this list from sheet
    #anthropic_models=["claude-3-opus-20240229"]
    
    #Anthropic
    if provider.lower() == "anthropic":
        logging.info(f"Using Anthropic model '{model_name}' with temperature {temperature}.")
        return ChatAnthropic(
            model_name  = model_name,                            #use model_name as endpoint
            api_key     = os.environ.get("ANTHROPIC_API_KEY"),
            temperature = temperature,
            #stop = ["\nObservation"] 
            )
    
    #Azure OpenaI   
    if provider.lower() == "azure_openai":
        logging.info(f"Using Azure model '{model_name}' with temperature {temperature}.")
        return AzureChatOpenAI(
            azure_deployment = deployment,                            
            azure_endpoint   = base_url,                              #os.environ.get("AZURE_OPENAI_ENDPOINT"),
            api_key          = os.environ.get("AZURE_OPENAI_KEY"),
            api_version=os.environ.get("AZURE_OPENAI_VERSION"),
            temperature=temperature
            )

    #OpenAI
    if provider.lower() == "openai":
        logging.info(f"Using OpenAI model '{model_name}' with temperature {temperature}.")
        return ChatOpenAI(
            model           = model_name, 
            temperature     = temperature,
            base_url        = base_url,
            )
    #Groq
    if provider.lower() == "groq":
        logging.info(f"Using Groq model '{model_name}' with temperature {temperature}.")
        return ChatGroq(
            model           = model_name, 
            temperature     = temperature,
            #base_url        = base_url,
            )
    
    #Ollama - Don't check providor, yet
 

    def find_matching_model(model_name, existing_models):
        """
        Finds a matching model from the list of existing models.
        Supports both exact matches and base model matches when a version is not specified.
        """
        # Handle model names that include specific versions
        if ':' in model_name:
            for model in existing_models:
                if model['name'] == model_name:
                    logging.info(f"Specific version '{model_name}' found in Ollama, loading directly.")
                    return model
        else:
            # Handle base model names without specific versions
            base_model_name = model_name.split(':')[0]
            for model in existing_models:
                if model['name'].startswith(base_model_name + ':'):
                    logging.info(f"Base model for '{base_model_name}' exists in Ollama, loading: {model['name']}")
                    return model
        return None

    def pull_and_load_model(model_name, progress, llm_task):
        """
        Attempts to pull a model and handle progress updates.
        """
        try:
            for progress_update in pull(model_name, stream=True):
                handle_progress_updates(progress_update, progress, llm_task)
            
            logging.info(f"Model '{model_name}' successfully pulled and loaded.")
            return ollama_mod_and_load(model=model_name)
        except Exception as e:
            logging.error(f"Failed to pull the model '{model_name}' with Ollama. Error: {str(e)}")
            return None

    def handle_progress_updates(progress_update, progress, llm_task):
        """
        Handles progress updates during model download and initialization.
        """
        if 'total' in progress_update:
            progress.update(llm_task, total=progress_update['total'])
        if 'completed' in progress_update:
            current_completed = progress.tasks[llm_task].completed
            new_advance = progress_update['completed'] - current_completed
            progress.advance(llm_task, advance=new_advance)
        if 'status' in progress_update:
            progress.update(llm_task, advance=0, description=f"[cyan]{progress_update['status']}")


    """
    Retrieves a language model by name, handling version specifics and streaming updates.
    """
    existing_models = list()['models']
    matching_model = find_matching_model(model_name, existing_models)
    if matching_model:
        return ollama_mod_and_load(model = matching_model['name'], num_ctx = num_ctx)
    
    logging.info(f"Model '{model_name}' not found in Ollama. Attempting to pull with streaming enabled.")
    return pull_and_load_model(model_name, progress, llm_task)


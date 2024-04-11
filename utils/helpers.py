def greetings_print():
    print("\n\n============================= Starting crewai-sheets-ui =============================\n")
    print("Copy this sheet template and create your agents and tasks:\n")
    print("https://docs.google.com/spreadsheets/d/1a5MBMwL9YQ7VXAQMtZqZQSl7TimwHNDgMaQ2l8xDXPE\n")
    print("======================================================================================\n\n")

def after_read_sheet_print(agents_df, tasks_df):
    print("\n\n=======================================================================================\n")
    print(f""""Found the following agents in the spreadsheet: \n {agents_df}""")
    print(f""""\nFound the following tasks in the spreadsheet: \n {tasks_df}""")
    print(f"\n=============================Welcome to the {agents_df['Team Name'][0]} Crew ================= \n\n")
                                                                                                            
def str_to_bool(value_str):
    if isinstance(value_str, bool):
        return value_str
    else:
        return value_str.lower() in ['true', '1', 't', 'y', 'yes']


import os
from dotenv import load_dotenv
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




import  logging
import  subprocess
from    langchain_community.llms import Ollama
from    langchain_openai         import ChatOpenAI

def get_llm(model_name, temperature=0.7):
    """
    Returns the appropriate LLM based on the model name and temperature.
    
    :param model_name: The name of the model to load.
    :param temperature: The temperature setting for the model.
    :return: An instance of the LLM.
    """
    # Define OpenAI models for direct use with the OpenAI API
    openai_models = ["gpt-3.5-turbo", "gpt-4-turbo-preview"]
    
    if model_name in openai_models:
        # For recognized OpenAI models, return a ChatOpenAI instance with specified temperature
        logging.info(f"Using OpenAI model '{model_name}' with temperature {temperature}.")
        return ChatOpenAI(model=model_name, temperature=temperature)
    else:
        # For other models, pull the model using Ollama and return an Ollama instance
        logging.info(f"Attempting to pull the model '{model_name}' using Ollama. Please wait...")
        command = ["ollama", "pull", model_name]
        result = subprocess.run(command)
        
        if result.returncode == 0:
            logging.info(f"Model '{model_name}' successfully pulled with Ollama.")
            return Ollama(model=model_name)  # Note: Assuming Ollama's API allows setting temperature, adjust as necessary
        else:
            logging.error(f"\n⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\
                            \nFailed to pull the model '{model_name}' with Ollama. Is Ollama service running?  \
                            \n(hint: Ollama serve)\n\n ⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯")
            return None

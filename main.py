import  os
import logging
from dotenv import load_dotenv
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
os.environ['ANONYMIZED_TELEMETRY']  = 'False'                       # Disable interpreter telemetry
os.environ['EC_TELEMETRY']          = 'False'                       # Disable embedchain telemetry
os.environ['HAYSTACK_TELEMETRY_ENABLED'] = "False"                  # Disable crewai telemetry
                   # Load API keys from ENV #Gives nice error if listed ENV variables are not set

from textwrap           import dedent
from crewai             import Crew, Task, Agent, Process


#from langchain_community.llms import OpenAI
from langchain_community.llms import Ollama
from langchain_community.llms import LlamaCpp
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from utils.helpers   import get_llm

#crewai-sheets-ui
from tools.tools        import ToolsMapping
from utils              import Sheets
from utils              import helpers
from rich.console       import Console
from rich.progress      import Progress
from rich.table         import Table
from rich.console       import Console

import  argparse
import signal
import sys

# Define a function to handle termination signals
def signal_handler(sig, frame):
    print("\n\nReceived termination signal. Shutting down gracefully...\n\n")
    # Perform cleanup actions here
    # Close connections, release resources, etc.
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Helper function to create agents
def create_agents_from_df(row, progress, agent_task, llm_task):
    model_name = row.get('Model Name', 'gpt-4-turbo-preview').strip()
    temperature = float(row.get('Temperature', 0.7))
    num_ctx = int(row.get('Context size', 2048))

    llm = get_llm(model_name, temperature, progress, llm_task, num_ctx=num_ctx)
    if llm is None:
        raise ValueError(f"Failed to retrieve or initialize the language model for {model_name}")

    def get_agent_tools(tools_string):
        tool_names = [tool.strip() for tool in tools_string.split(',')]
        return [getattr(ToolsMapping, tool) for tool in tool_names if hasattr(ToolsMapping, tool)]

    agent_config = {
        #agent_executor:                                            #An instance of the CrewAgentExecutor class.
        'role'            : row['Agent Role'],
        'goal'            : dedent(row['Goal']),
        'backstory'       : dedent(row['Backstory']),
        'allow_delegation': helpers.str_to_bool(row['Allow delegation']),   #Whether the agent is allowed to delegate tasks to other agents.
        'verbose'         : helpers.str_to_bool(row['Verbose']),            #Whether the agent execution should be in verbose mode.
        'tools'           : get_agent_tools(row['Tools']),          #Tools at agents disposal
        'memory'          : True,                                   #TODO: Remove hardcoding #Whether the agent should have memory or not.
        'max_iter'        : 2000,                                   #TODO: Remove hardcoding #Maximum number of iterations for an agent to execute a task.
        'llm'             : llm,                                    #The language model that will run the agent.
        'function_calling_llm': llm                                 #The language model that will the tool calling for this agent, it overrides the crew function_calling_llm.
        #step_callback:                                             #Callback to be executed after each step of the agent execution.
        #callbacks:                                                 #A list of callback functions from the langchain library that are triggered during the agent's execution process
    }                                                               
    progress.update(agent_task, advance=1)
    return Agent(config = agent_config)      
        
def get_agent_by_role(agents, desired_role):
    return next((agent for agent in agents if agent.role == desired_role), None)
            
def create_tasks_from_df(row, assignment, created_agents):
    description     = row['Instructions'].replace('{assignment}', assignment)
    desired_role    = row['Agent']

    return Task(
        description         = dedent(description),
        expected_output     = row['Expected Output'],
        agent               = get_agent_by_role(created_agents, desired_role)
    )

def create_crew(created_agents, created_tasks):
    return Crew(
        agents  =created_agents,
        tasks   =created_tasks,
        verbose =True,               #TODO remove hardcoding
        process =Process.sequential, #TODO remove hardcoding
        memory = True,               #TODO remove hardcoding 
        embedder={                   #TODO remove hardcoding  
			"provider": "azure_openai",#TODO make this configurable
			"config":{
				"model": 'text-embedding-ada-002',#TODO make this configurable
				"deployment_name": "text-embedding-ada-002",#TODO make this configurable and optional
			}
        }
    )


if __name__ == "__main__":

    #Parse comman line arguments
    parser  = argparse.ArgumentParser()
    parser.add_argument('--sheet_url', help='The URL of the google sheet')
    parser.add_argument('--env_path', default=".env", help='The path to the .env file')

    args    = parser.parse_args()

    if args.sheet_url:
        sheet_url = args.sheet_url
    else:
        helpers.greetings_print()                                          #shows google sheets template file.
        sheet_url = input("Please provide the URL of your google sheet:")

    load_dotenv(args.env_path)

    agents_df, tasks_df = Sheets.parse_table(sheet_url)
    helpers.after_read_sheet_print(agents_df, tasks_df)                     #Print overview of agents and tasks
    
    console = Console()
    progress = Progress(transient=True)
   

    with Progress() as progress:
        agent_task = progress.add_task("[cyan]Creating agents......", total=len(agents_df))   #Agent progress bar  
        llm_task = progress.add_task("[cyan]  Pulling llm model...", total=100)  # 100 is a placeholder    
        agents_df['crewAIAgent'] = agents_df.apply(lambda row: create_agents_from_df(row, progress=progress, agent_task=agent_task, llm_task=llm_task), axis=1)
        created_agents = agents_df['crewAIAgent'].tolist()
        
        
        task_task = progress.add_task("[cyan]Creating tasks...", total=1)                   #Task progress bar
        assignment = tasks_df['Assignment'][0]
        tasks_df['crewAITask'] = tasks_df.apply(lambda row: create_tasks_from_df(row, assignment, created_agents), axis=1)
        created_tasks = tasks_df['crewAITask'].tolist()
        progress.advance(task_task)
        
        # Creating crew
        crew_task = progress.add_task("[cyan]Creating crew...", total=1)                    #Crew progress bar
        crew = create_crew(created_agents, created_tasks)
        progress.advance(crew_task)
        
        progress.stop
        console.print("[green]Crew created successfully!")

    results = crew.kickoff()

    terminal_width = console.width

   # Ensure the terminal width is at least 120 characters
    terminal_width = max(terminal_width, 120)

    # Create a table for results
    result_table = Table(show_header=True, header_style="bold magenta")
    result_table.add_column("Here are the results", style="green", width=terminal_width)

    
    result_table.add_row(str(results))

    console.print(result_table)
    console.print("[bold green]\n\n")


 # #llm =ChatOpenAI(    
    #     #base_url       = "http://localhost:1234/v1",
    #     #api_key        = "lm-studio",
    #     #callback_manager= callback_manager,
    #     #max_tokens     = -1,
    #     #streaming      = True,
    #     #verbose        = True, 
    #     #Not available in OpenAI: n_predict = -1, top_k = 40, repeat_penalty= 1.1, min_p= 0.05
    #     model_name     = "gpt-4-turbo-preview",
    #     temperature    = 0.9,
    #     #model_kwargs={
    #                     #"n_predict":-1,
    #                     #"top_k":40,
    #                     #"repeat_penalty":1.24,
    #                     #"min_p":0.05,
    #                     #"top_p":0.95,
    #                     #}
    #     )



 
       #callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])  # Callbacks support token-wise streaming

        #Agent LLM fields
        #model_name     = row.get('Model Name', 'gpt-4-turbo-preview') #Selection of model for OpenAI. Or HuggingFace Model name for caching (via llamacpp)
        #temperature    = float(row.get('Temperature', 0.0))
        #base_url       = row.get('Base URL', None)                    #For "local" OpenAI compatible LLM  
        #chat_format    = "vicuna"                                     # or "llama-2", vicuna,  etc.., for llama-cpp-python //TODO remove hardcoding. 
        #llm_params = {'model_name': model_name, 'temperature': temperature}
        #Adjust the instantiation based on whether a base URL is provided
        #if base_url is not None and base_url == base_url:  # if base_url is not NaN...
        #       llm_params['base_url'] = base_url
        #       max_tokens = 2048 #//TODO Remove hardcoding
        #llm_params['max_tokens'] = max_tokens
        
    #Function calling LLM fields
    #FOR LLAMACPP CONFIG
    #llm = LlamaCpp(
    #   #model_path="./../llama.cpp/models/Hermes-2-Pro-Mistral-7B-GGUF/Hermes-2-Pro-Mistral-7B.Q8_0.gguf",
    #   #model_path="./../../../.cache/lm-studio/models/mradermacher/Nous-Capybara-limarpv3-34B-i1-GGUF/Nous-Capybara-limarpv3-34B.i1-Q4_K_M.gguf",
    #   callback_manager    = callback_manager,
    #   verbose             = True,  # Verbose is required to pass to the callback manager
    #   streaming           = True, 
    #   n_gpu_layers        = -1,
    #   n_threads           = 4,
    #   f16_kv              = True,  # MUST set to True, otherwise you will run into problem after a couple of calls
    #   n_ctx               = 36000, #defined by model
    #   n_batch             = 2048,
    #   max_new_tokens      = 512,
    #   max_length          = 4096,
    #   last_n_tokens_size  = 1024,
    #   temperature         = 0.0, 
    #   chat_template       = "[INST] <<SYS>>\n{system}\n<</SYS>>\n\n{instruction} [/INST]",
    #                         #{System}\nUSER: {user}\nASSISTANT: {response}</s>",
    #   chat_format         = "llama-2",
    #   max_tokens          = 256, 
    #   top_p               = 0.5,
    #   top_k               = 10,
    #   use_mlock           = True,
    #   repeat_penalty      = 1.5,
    #   seed                = -1,
    #   model_kwargs        = {"model_name":"01-ai/Yi-34B", "offload_kqv":True, "min_p":0.05},
    #   stop                = ["\nObservation"],     
    # )
        # print("\nCreating agents:.\n")
    # agents_df['crewAIAgent'] = agents_df.apply(create_agents_from_df, axis=1)
    # created_agents = agents_df['crewAIAgent'].tolist()

    # print("Creating tasks:..\n")
    # assignment = tasks_df['Assignment'][0]
    # tasks_df['crewAITask'] = tasks_df.apply(lambda row: create_tasks_from_df(row, assignment, created_agents), axis=1)
    # created_tasks = tasks_df['crewAITask'].tolist()
    
    # print("Creating crew:...\n")
    # crew = create_crew(created_agents, created_tasks)
    # results = crew.kickoff()

    # Print results
from dotenv import load_dotenv
load_dotenv() #Export API keys from .env

#Reading from google sheets
from utils import Sheets
import re

#CrewAI
from langchain_openai import ChatOpenAI #in case we want to load a local LLM
from crewai import Crew, Task, Agent, Process
from textwrap import dedent


#crewai-sheets-ui Tools:
from tools import FileTool, CLITool

from crewai_tools import SeleniumScrapingTool
scrape_tool = SeleniumScrapingTool()

#from crewai_tools import FileReadTool
#file_read_tool = FileReadTool()

#human tools
from langchain.agents.load_tools import load_tools
human_tools = load_tools(["human"])[0]   #human tools come as an array. So easiest to just get the firdt element.

#duck duck go tool
from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchResults
search = DuckDuckGoSearchResults()


class_mapping = {
	    'Executor': CLITool.execute_cli_command,
		'File Tool': FileTool.manage_file, 
		'Search Internet': search, #search_tool,
		'scrape_website': scrape_tool,#websitesc_search_tool,
		'human_tools': human_tools                  
		}	

sheet_url = input("Please provide the URL of the google sheet:")
dataframes = Sheets.read_google_sheet(sheet_url)
Agents = dataframes[0]
Tasks = dataframes[1]

print(f""""Found the following agents in the spreadsheet: \n {Agents}""")
print(f""""Found the following Tasks in the spreadsheet: \n {Tasks}""")
print(f"## Welcome to the {Agents['Team Name'][0]} Crew")
print('------------------------------- \n')



print("Creating agents:")
created_agents = []
# Iterate over each agent
for index, agent in Agents.iterrows():
	non_printable_pattern = re.compile('[^\x20-\x7E]+')
	id_clean = re.sub(non_printable_pattern, '', agent['Agent Role']) # Remove non-printable characters
	id = id_clean.replace(' ', '_') # Replace spaces with underscores
	role = agent['Agent Role']
	goal = agent['Goal']
	backstory = agent['Backstory']
	tools_string = agent['Tools']
	allow_delegation = agent['Allow delegation']
	verbose = agent['Verbose']
	developer = agent['Developer']
	#make sure allow_delegation is bool
	if isinstance(allow_delegation, bool):
		allow_delegation_bool = allow_delegation
	else:
		allow_delegation_bool = True if allow_delegation.lower() in ['true', '1', 't', 'y', 'yes'] else False
	#make sure verbose is bool
	if isinstance(verbose, bool):
		verbose_bool = verbose
	else:
		verbose_bool = True if allow_delegation.lower() in ['true', '1', 't', 'y', 'yes'] else False
	#use class_mapping dictionary to replace tool strings with classes
	#tools = tools_string.split(',')
	tools = [tool.strip() for tool in tools_string.split(',')]
	print("######Tools Before \\nn")
	print(tools)
	
	tools = [class_mapping[tool] for tool in tools if tool in class_mapping]
	print("#####Tools After: \n\n")
	print(tools)
	#Finally crete the agent & append to created_agents
	new_agent = Agent(
			role=role,
			goal=dedent(goal),
			backstory=dedent(backstory),
			tools = tools,
            allow_delegation = allow_delegation_bool,
			verbose = verbose_bool,
			llm = ChatOpenAI(model_name="stabilityai/stable-code-instruct-3b", temperature=0.0, base_url="http://localhost:1234/v1") if developer 
					else ChatOpenAI(model_name="gpt-4-turbo-preview", temperature=0.2),
			function_calling_llm= ChatOpenAI(model_name="gpt-4-turbo-preview", temperature=0.2)

	)
	created_agents.append(new_agent)



def get_agent_by_role(agents, desired_role):
    return next((agent for agent in agents if agent.role == desired_role), None)

print("\nCreating tasks:")
created_tasks = []
assignment=Tasks['Assignment'][0] 
# Iterate over each task
for index, task in Tasks.iterrows():
	print(f"#Creating task {index}")
	description = task['Instructions'].replace('{assignment}', assignment)
	desired_role = task['Agent']

	new_task = Task(
		description=dedent(description),
		expected_output=task['Expected Output'],
		agent=get_agent_by_role(created_agents, desired_role)
			)
	created_tasks.append(new_task)

# Create Crew responsible for Copy
crew = Crew(
	agents=created_agents,
	tasks=created_tasks,
	verbose=True,
	process=Process.sequential
    #manager_llm=ChatOpenAI(model_name="gpt-4-turbo-preview", temperature=0.0)
)

assignment = crew.kickoff()


# Print results
print("\n\n########################")
print("## Here is the result")
print("########################\n")
print(assignment)

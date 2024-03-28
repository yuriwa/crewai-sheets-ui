from dotenv import load_dotenv
load_dotenv() #Export API keys from .env

#Reading from google sheets
from utils import Sheets
import re

#CrewAI
from langchain_openai import ChatOpenAI #in case we want to load a local LLM
from langchain.agents.load_tools import load_tools #in case we want to import some tools from langchain
from crewai import Crew, Task, Agent, Process
from textwrap import dedent

#Tool class imports
###CrewAI_tools
from crewai_tools import 	CodeDocsSearchTool	#	A RAG tool optimized for searching through code documentation and related technical documents.
from crewai_tools import	CSVSearchTool	#	A RAG tool designed for searching within CSV files, tailored to handle structured data.
from crewai_tools import	DirectorySearchTool	#	A RAG tool for searching within directories, useful for navigating through file systems.
from crewai_tools import	DOCXSearchTool	#	A RAG tool aimed at searching within DOCX documents, ideal for processing Word files.
from crewai_tools import	DirectoryReadTool	#	Facilitates reading and processing of directory structures and their contents.
from crewai_tools import	FileReadTool	#	Enables reading and extracting data from files, supporting various file formats.
from crewai_tools import	GithubSearchTool	#	A RAG tool for searching within GitHub repositories, useful for code and documentation search.
#from crewai_tools import	SeperDevTool	#	A specialized tool for development purposes, with specific functionalities under development.
from crewai_tools import	TXTSearchTool	#	A RAG tool focused on searching within text (.txt) files, suitable for unstructured data.
from crewai_tools import	JSONSearchTool	#	A RAG tool designed for searching within JSON files, catering to structured data handling.
from crewai_tools import	MDXSearchTool	#	A RAG tool tailored for searching within Markdown (MDX) files, useful for documentation.
from crewai_tools import	PDFSearchTool	#	A RAG tool aimed at searching within PDF documents, ideal for processing scanned documents.
from crewai_tools import	PGSearchTool	#	A RAG tool optimized for searching within PostgreSQL databases, suitable for database queries.
from crewai_tools import	RagTool	#	A general-purpose RAG tool capable of handling various data sources and types.
from crewai_tools import	ScrapeElementFromWebsiteTool	#	Enables scraping specific elements from websites, useful for targeted data extraction.
from crewai_tools import	ScrapeWebsiteTool	#	Facilitates scraping entire websites, ideal for comprehensive data collection.
from crewai_tools import	WebsiteSearchTool	#	A RAG tool for searching website content, optimized for web data extraction.
from crewai_tools import	XMLSearchTool	#	A RAG tool designed for searching within XML files, suitable for structured data formats.
from crewai_tools import	YoutubeChannelSearchTool	#	A RAG tool for searching within YouTube channels, useful for video content analysis.
from crewai_tools import	YoutubeVideoSearchTool	#	A RAG tool aimed at searching within YouTube videos, ideal for video data extraction.

###Langchain community tools 
from langchain_community.tools.ddg_search.tool \
				  import 	DuckDuckGoSearchResults #Gets search results from Duck Duck Go.

####crewai-sheets-ui Tools:
from tools 		import FileTool 	#Create, read, and edit a file line by line
from tools 		import CLITool		#Interpreter wrapper. Execure any command on the computer

#crewai--------------------------------------------
code_docs_search_tool 	= CodeDocsSearchTool()
csv_search_tool 		= CSVSearchTool()
directory_search_tool 	= DirectorySearchTool()
docx_earch_tool 		= DOCXSearchTool()
directory_read_tool 	= DirectoryReadTool()
file_read_tool 			= FileReadTool()
github_search_tool		= GithubSearchTool(content_types=['code', 'repo', 'pr', 'issue']) # Options: code, repo, pr, issue)
#seper_dev_tool			= SeperDevTool
txt_search_tool			= TXTSearchTool()
json_search_tool		= JSONSearchTool()
mdx_search_tool			= MDXSearchTool()
pdf_search_tool			= PDFSearchTool()
#pg_search_tool			= PGSearchTool()
rag_tool				= RagTool()
scrape_element_from_website_tool = ScrapeElementFromWebsiteTool()
scrape_website_tool		= ScrapeWebsiteTool()
website_search_tool		= WebsiteSearchTool()
xml_search_tool			= XMLSearchTool()
youtube_channel_search_tool = YoutubeChannelSearchTool()
youtube_video_search_tool =	YoutubeVideoSearchTool()
#langchain------------------------------------------
human_tools = load_tools(["human"])[0]   #A Tool that allows the Agents to talk to the human. 
search = DuckDuckGoSearchResults() #duck duck go Search
#crewai--sheets-ui
#file_tool = FileTool.manage_file()
#executor_tool=CLITool.execute_cli_command()

class_mapping = {
		'code_docs_search_tool'	:code_docs_search_tool, 	#A RAG tool optimized for searching through code documentation and related technical documents.
		'csv_search_tool'		:csv_search_tool, 			#A RAG tool designed for searching within CSV files, tailored to handle structured data.
		'directory_search_tool'	:directory_search_tool, 	#A RAG tool for searching within directories, useful for navigating through file systems.
		'docx_earch_tool'		:docx_earch_tool, 			#A RAG tool aimed at searching within DOCX documents, ideal for processing Word files.
		'directory_read_tool'	:directory_read_tool, 		#Facilitates reading and processing of directory structures and their contents.
		'file_read_tool'		:file_read_tool, 			#Enables reading and extracting data from files, supporting various file formats.
		'github_search_tool'	:github_search_tool, 		#A RAG tool for searching within GitHub repositories, useful for code and documentation search.
		#'#seper_dev_tool'		:seper_dev_tool, 			#A specialized tool for development purposes, with specific functionalities under development.
		'txt_search_tool'		:txt_search_tool, 			#A RAG tool focused on searching within text (.txt) files, suitable for unstructured data.
		'json_search_tool'		:json_search_tool, 			#A RAG tool designed for searching within JSON files, catering to structured data handling.
		'mdx_search_tool'		:mdx_search_tool, 			#A RAG tool tailored for searching within Markdown (MDX) files, useful for documentation.
		'pdf_search_tool'		:pdf_search_tool, 			#A RAG tool aimed at searching within PDF documents, ideal for processing scanned documents.
		#'pg_search_tool'		:PGSearchTool()., #pg_search_tool, 			#A RAG tool optimized for searching within PostgreSQL databases, suitable for database queries.
		'rag_tool'				:rag_tool, 					#A general-purpose RAG tool capable of handling various data sources and types.
		'scrape_element_from_website_tool':scrape_element_from_website_tool, #Enables scraping specific elements from websites, useful for targeted data extraction.
		'scrape_website_tool'	:scrape_website_tool, 		#Facilitates scraping entire websites, ideal for comprehensive data collection.
		'website_search_tool'	:website_search_tool, 		#A RAG tool for searching website content, optimized for web data extraction.
		'xml_search_tool'		:xml_search_tool, 			#A RAG tool designed for searching within XML files, suitable for structured data formats.
		'youtube_channel_search_tool' :youtube_channel_search_tool, #A RAG tool for searching within YouTube channels, useful for video content analysis.
		'youtube_video_search_tool' :youtube_video_search_tool, #A RAG tool aimed at searching within YouTube videos, ideal for video data extraction.
		#langchain------------------------------------------ 
		'human_tools'			:human_tools, 				#A Tool that allows the Agents to talk to the human. 
		'search'				:search, 					#Duck duck go Search
		#crewai--sheets-ui
		'executor'				:CLITool.execute_cli_command, #executor_tool,  			#interpreter CLI command
		'file_tool'				:FileTool.manage_file				#Create, read, and edit a file line by line     
}


print("\n\n============================= Starting crewai-sheets-ui =============================\n")
print("Copy this sheet template and create your agents and tasks:\n")
print("https://docs.google.com/spreadsheets/d/1a5MBMwL9YQ7VXAQMtZqZQSl7TimwHNDgMaQ2l8xDXPE\n")
print("======================================================================================\n\n")
sheet_url = input("Please provide the URL of your google sheet:")
dataframes = Sheets.read_google_sheet(sheet_url)
Agents = dataframes[0]
Tasks = dataframes[1]

print("\n\n=======================================================================================\n")
print(f""""Found the following agents in the spreadsheet: \n {Agents}""")
print(f""""\nFound the following Tasks in the spreadsheet: \n {Tasks}""")
print(f"\n=============================Welcome to the {Agents['Team Name'][0]} Crew ============================= \n\n") 
 
print("Creating agents:\n")
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
	
	tools = [tool.strip() for tool in tools_string.split(',')]
	tools = [class_mapping[tool] for tool in tools if tool in class_mapping]
	
	#Finally crete the agent & append to created_agents
	new_agent = Agent(
			role=role,
			goal=dedent(goal),
			backstory=dedent(backstory),
			tools = tools,
            allow_delegation = allow_delegation_bool,
			verbose = verbose_bool,
			max_iter=1000, #//TODO: remove hardcoding
			llm = ChatOpenAI(model_name="gpt-4-turbo-preview", temperature=0.0, base_url="http://localhost:1234/v1") if developer 
					else ChatOpenAI(model_name="gpt-4-turbo-preview", temperature=0.2),
			function_calling_llm= ChatOpenAI(model_name="gpt-4-turbo-preview", temperature=0.2)

	)
	created_agents.append(new_agent)



def get_agent_by_role(agents, desired_role):
    return next((agent for agent in agents if agent.role == desired_role), None)

print("\n============================= Creating tasks: =============================\n")
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


print("\n============================= Engaging the crew =============================\n\n")

crew = Crew(
	agents=created_agents,
	tasks=created_tasks,
	verbose=True,
	process=Process.sequential
    #manager_llm=ChatOpenAI(model_name="gpt-4-turbo-preview", temperature=0.0)
)

assignment = crew.kickoff()


# Print results
print("\n\n ============================= Here is the result =============================\n\n")
print(assignment)

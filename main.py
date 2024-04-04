import re
from textwrap import dedent
from crewai import Crew, Task, Agent, Process

from langchain_openai import ChatOpenAI  # for loading a local LLM

from tools.tools import ToolsMapping
from utils import Sheets


def parse_table(url="https://docs.google.com/spreadsheets/d/1a5MBMwL9YQ7VXAQMtZqZQSl7TimwHNDgMaQ2l8xDXPE"):
    dataframes = Sheets.read_google_sheet(url)
    Agents = dataframes[0]
    Tasks = dataframes[1]
    return Agents, Tasks


def greetings_print():
    print("\n\n============================= Starting crewai-sheets-ui =============================\n")
    print("Copy this sheet template and create your agents and tasks:\n")
    print("https://docs.google.com/spreadsheets/d/1a5MBMwL9YQ7VXAQMtZqZQSl7TimwHNDgMaQ2l8xDXPE\n")
    print("======================================================================================\n\n")


def after_read_sheet_print(agents_df, tasks_df):
    print("\n\n=======================================================================================\n")
    print(f""""Found the following agents in the spreadsheet: \n {agents_df}""")
    print(f""""\nFound the following tasks in the spreadsheet: \n {tasks_df}""")
    print(
        f"\n=============================Welcome to the {agents_df['Team Name'][0]} Crew ============================= \n\n")


def get_agent_by_role(agents, desired_role):
    return next((agent for agent in agents if agent.role == desired_role), None)


def create_agents_from_df(row):
    non_printable_pattern = re.compile('[^\x20-\x7E]+')
    id_clean = re.sub(non_printable_pattern, '', row['Agent Role'])  # Remove non-printable characters
    id = id_clean.replace(' ', '_')  # Replace spaces with underscores
    role = row['Agent Role']
    goal = row['Goal']
    backstory = row['Backstory']
    tools_string = row['Tools']
    allow_delegation = row['Allow delegation']
    verbose = row['Verbose']

    # Convert 'Allow delegation' and 'Verbose' to boolean
    allow_delegation_bool = True if str(allow_delegation).lower() in ['true', '1', 't', 'y', 'yes'] else False
    verbose_bool = True if str(verbose).lower() in ['true', '1', 't', 'y', 'yes'] else False

    tools_names = [tool.strip() for tool in tools_string.split(',')]
    tools = [getattr(ToolsMapping, tool) for tool in tools_names if hasattr(ToolsMapping, tool)]

    # Parse LLM configuration
    model_name = row.get('Model Name', 'gpt-4-turbo-preview')
    temperature = float(row.get('Temperature', 0.2))
    base_url = row.get('Base URL', None)

    llm_params = {'model_name': model_name, 'temperature': temperature}

    # Adjust the instantiation based on whether a base URL is provided
    if base_url is not None and base_url == base_url:  # NaN is not equal to itself
        llm_params['base_url'] = base_url
    llm = ChatOpenAI(**llm_params)

    return Agent(
        role=role,
        goal=dedent(goal),
        backstory=dedent(backstory),
        tools=tools,
        allow_delegation=allow_delegation_bool,
        verbose=verbose_bool,
        llm=llm
    )


def create_tasks_from_df(row, assignment, created_agents):
    description = row['Instructions'].replace('{assignment}', assignment)
    desired_role = row['Agent']

    return Task(
        description=dedent(description),
        expected_output=row['Expected Output'],
        agent=get_agent_by_role(created_agents, desired_role)
    )


def create_crew(created_agents, created_tasks):
    print("\n============================= Engaging the crew =============================\n\n")

    return Crew(
        agents=created_agents,
        tasks=created_tasks,
        verbose=True,
        process=Process.sequential
    )


if __name__ == "__main__":
    from dotenv import load_dotenv
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--sheet_url', help='The URL of the google sheet')
    args = parser.parse_args()

    load_dotenv()
    greetings_print()
    if args.sheet_url:
        sheet_url = args.sheet_url
    else:
        sheet_url = input("Please provide the URL of your google sheet:")
    agents_df, tasks_df = parse_table(sheet_url)
    after_read_sheet_print(agents_df, tasks_df)

    print("Creating agents:\n")
    agents_df['crewAIAgent'] = agents_df.apply(create_agents_from_df, axis=1)
    created_agents = agents_df['crewAIAgent'].tolist()

    print("\n============================= Creating tasks: =============================\n")
    assignment = tasks_df['Assignment'][0]
    tasks_df['crewAITask'] = tasks_df.apply(lambda row: create_tasks_from_df(row, assignment, created_agents), axis=1)

    created_tasks = tasks_df['crewAITask'].tolist()
    crew = create_crew(created_agents, created_tasks)
    results = crew.kickoff()

    # Print results
    print("\n\n ============================= Here is the result =============================\n\n")
    print(assignment)

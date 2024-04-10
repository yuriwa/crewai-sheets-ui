def greetings_print():
    print("\n\n============================= Starting crewai-sheets-ui =============================\n")
    print("Copy this sheet template and create your agents and tasks:\n")
    print("https://docs.google.com/spreadsheets/d/1a5MBMwL9YQ7VXAQMtZqZQSl7TimwHNDgMaQ2l8xDXPE\n")
    print("======================================================================================\n\n")

def after_read_sheet_print(agents_df, tasks_df):
    print("\n\n=======================================================================================\n")
    print(f""""Found the following agents in the spreadsheet: \n {agents_df}""")
    print(f""""\nFound the following tasks in the spreadsheet: \n {tasks_df}""")
    print(f"\n=============================Welcome to the {agents_df['Team Name'][0]} Crew ============================= \n\n")

def str_to_bool(value_str):
    if isinstance(value_str, bool):
        return value_str
    else:
        return value_str.lower() in ['true', '1', 't', 'y', 'yes']

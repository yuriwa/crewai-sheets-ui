import pandas as pd

class Sheets:
    @staticmethod
    def read_google_sheet(sheet_url):
        # Extract the base URL from the provided Google Sheet URL
        base_url = sheet_url.split('/edit')[0]
        dataframes = []

        # Define the worksheets and their respective columns to be read
        worksheets = {
            'Agents': ['Agent Role', 'Goal', 'Backstory', 'Tools', 'Allow delegation', 'Verbose', 'Memory', 'Max_iter','Model Name', 'Temperature', 'Function Calling Model'],
            'Tasks' : ['Task Name', 'Agent', 'Instructions', 'Expected Output'],
            'Crew'  : ['Team Name',	'Assignment','Verbose', 'Process', 'Memory', 'Embedding model', 'Manager LLM', 't', 'num_ctx'],
            'Models': ['Model', 'Context size (local only)', 'Provider', 'base_url','Deployment']
        }

        # Iterate over the worksheets to read the required data
        for worksheet, columns in worksheets.items():
            # Construct the URL for downloading the worksheet as CSV
            url = f'{base_url}/gviz/tq?tqx=out:csv&sheet={worksheet}'

            # Read the worksheet into a DataFrame, selecting only the specified columns
            try:
                data = pd.read_csv(url, usecols=columns)
                if worksheet == 'Agents':
                    data['Function Calling Model'] = data['Function Calling Model'].replace("None", None)
                if worksheet == 'Models':
                    data['Context size (local only)'] = data['Context size (local only)'].replace(0, None)
                    data['base_url'] = data['base_url'].replace("None", None)
                    data['Deployment'] = data['Deployment'].replace("None", None)
                if worksheet == "Crew":
                    data['Embedding model'] = data['Embedding model'].replace("None", None)
                    data['Manager LLM'] = data['Manager LLM'].replace("None", None)
                    data['t'] = data['t'].replace(0, None)
                    data['num_ctx'] = data['num_ctx'].replace(0, None)
            except ValueError as e:
                # Handle cases where specified columns are not found in the sheet
                print(f"\nError reading worksheet '{worksheet}'. MAke sure all fields have a value. Use None or 0 if no value needed {e}")
                continue

            data = data.where(pd.notnull(data), None) # Replace NaN values with None
            # Append the DataFrame to the list of dataframes
            dataframes.append(data)

        return dataframes
    
    @staticmethod
    def parse_table(url="https://docs.google.com/spreadsheets/d/1a5MBMwL9YQ7VXAQMtZqZQSl7TimwHNDgMaQ2l8xDXPE"):
        dataframes  = Sheets.read_google_sheet(url)
        Agents      = dataframes[0]
        Tasks       = dataframes[1]
        Crew        = dataframes[2]
        Models      = dataframes[3]
        return Agents, Tasks, Crew, Models

import pandas as pd

class Sheets:
    @staticmethod
    def read_google_sheet(sheet_url):
        # Extract the base URL from the provided Google Sheet URL
        base_url = sheet_url.split('/edit')[0]
        dataframes = []

        # Define the worksheets and their respective columns to be read
        worksheets = {
            'Agents': ['Team Name', 'Agent Role', 'Goal', 'Backstory', 'Tools', 'Allow delegation', 'Verbose', 'Model Name', 'Temperature', 'Base URL', 'Context size'],
            'Tasks': ['Task Name', 'Agent', 'Instructions', 'Expected Output', 'Assignment']
        }

        # Iterate over the worksheets to read the required data
        for worksheet, columns in worksheets.items():
            # Construct the URL for downloading the worksheet as CSV
            url = f'{base_url}/gviz/tq?tqx=out:csv&sheet={worksheet}'

            # Read the worksheet into a DataFrame, selecting only the specified columns
            try:
                data = pd.read_csv(url, usecols=columns)
            except ValueError as e:
                # Handle cases where specified columns are not found in the sheet
                print(f"Error reading worksheet '{worksheet}': {e}")
                continue

            # Append the DataFrame to the list of dataframes
            dataframes.append(data)

        return dataframes
    
    @staticmethod
    def parse_table(url="https://docs.google.com/spreadsheets/d/1a5MBMwL9YQ7VXAQMtZqZQSl7TimwHNDgMaQ2l8xDXPE"):
        dataframes  = Sheets.read_google_sheet(url)
        Agents      = dataframes[0]
        Tasks       = dataframes[1]
        return Agents, Tasks

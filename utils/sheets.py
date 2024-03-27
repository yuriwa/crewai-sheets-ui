import pandas as pd

class Sheets:
    def read_google_sheet(sheet_url):
        base_url = sheet_url.split('/edit')[0]
        dataframes = []
        worksheets = {
            'Agents': ['Team Name', 'Agent Role', 'Goal', 'Backstory', 'Tools', 'Allow delegation', 'Verbose', 'Developer'],
            'Tasks': ['Task Name', 'Agent', 'Instructions', 'Expected Output', 'Assignment']
        }
        for worksheet, columns in worksheets.items():
            url = f'{base_url}/gviz/tq?tqx=out:csv&sheet={worksheet}'
            data = pd.read_csv(url, usecols=columns)
            dataframes.append(data)
        return dataframes


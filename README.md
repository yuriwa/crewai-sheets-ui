# crewai-sheets-ui Project

## Overview
The crewai-sheets-ui project is designed to automate the process of reading data from a Google Sheet, creating agents and tasks based on that data, and executing those tasks. This project utilizes a combination of external libraries and custom tools to manage and execute tasks efficiently.

## Setup
1. Clone the repository.
2. Install the required dependencies by running `pip install -r requirements.txt`.
3. Set up a `.env` file in the root directory with your API keys and other environment variables.

## Usage
To use the project, provide the URL of the Google Sheet when prompted. The script will read the data, create agents and tasks, and execute them accordingly.

## Dependencies
- dotenv
- langchain_openai
- crewai
- crewai[tools]
- pandas

For a complete list of dependencies, refer to the `requirements.txt` file.

## Contributing
Contributions to the crewai-sheets-ui project are welcome. Please ensure to follow the project's code of conduct and submit pull requests for any enhancements or bug fixes.

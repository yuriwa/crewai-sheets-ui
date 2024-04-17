![# crewai-sheets-ui Project](https://repository-images.githubusercontent.com/778369177/0b532ef9-0315-49f6-9edf-83496ae0f399)

## Overview
The `crewai-sheets-ui` project automates the process of integrating Google Sheets data to dynamically create and execute tasks and agents. This system leverages a mix of external libraries and proprietary tools to efficiently handle task management and execution.

## Setup
To get started with the project, follow these steps:
1. Clone the repository:
   ```
   git clone https://github.com/yuriwa/crewai-sheets-ui.git
   ```
2. Navigate to the project directory:
   ```
   cd crewai-sheets-ui
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Create and configure an `.env` file in the project's root directory for storing API keys and other environment variables:
   - Rename `example.env`:
     ```
     mv example.env .env
     ```
   - Edit `.env` with your specific configurations.
5. Start the application:
   ```
   python ./main.py
   ```

## Usage
Launch the application and input the URL of your Google Sheet when prompted. The script will process the data to generate tasks and agents, which are then executed automatically.

### Advanced Usage
By default, the Agent and Crew memory features are enabled. To customize the memory settings, add the OpenAI API base URL and API key to the `.env` file or host your own model locally:
- `.env` example:
  ```
  OPENAI_API_BASE='http://localhost:8080/v1' #host and port where you local embed model is running
  OPENAI_MODEL_NAME='does-not-matter'
  OPENAI_API_KEY='111111111111111111111'
  ```
- To run your own model server, use:
  ```
  ./server -m {embedding-modelname} -c 32768 --verbose --embedding
  ```

## Dependencies
A range of packages are utilized in this project:
- crewai
- crewai-tools
- open-interpreter
- duckduckgo-search
- pandas
- ollama
- langchain_community
- rich

Refer to the `requirements.txt` file for a complete list of dependencies.

## Usage with Docker
Set up the project using Docker with these steps:
1. Install Docker for your operating system.
2. Download the Dockerfile:
   ```
   wget https://github.com/yuriwa/crewai-sheets-ui/blob/main/Dockerfile
   ```
3. Build the Docker image:
   ```
   docker build --no-cache -t crewai-image .
   ```
4. Run the Docker container:
   ```
   docker run -it -p 1234:1234 -v ${savefile/path/on/your/computer}:/home/user/root/savefiles -e OPENAI_API_KEY='{YOUR_OPENAI_API_KEY}' crewai-image
   ```

If opting to use a local language model server instead of OpenAI, host your server using LM Studio, llama.cpp or a similar tool.

## Contributing
Contributions to the crewai-sheets-ui project are welcome. Please ensure to follow the project's code of conduct and submit pull requests for any enhancements or bug fixes.

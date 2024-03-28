# crewai-sheets-ui Project

## Overview
The crewai-sheets-ui project is designed to automate the process of reading data from a Google Sheet, creating agents and tasks based on that data, and executing those tasks. This project utilizes a combination of external libraries and custom tools to manage and execute tasks efficiently.

## Setup
1. Clone the repository. `git clone https://github.com/yuriwa/crewai-sheets-ui.git`
2. Install the required dependencies by running `pip install -r requirements.txt`.
3. Set up a an .env file in the root directory with your API keys and other environment variables:
    - edit `example.env` and then
    - `mv example.env .env`


## Usage
To use the project, provide the URL of the Google Sheet when prompted. The script will read the data, create agents and tasks, and execute them accordingly.

## Dependencies
- dotenv
- langchain_openai
- crewai
- crewai[tools]
- pandas

For a complete list of dependencies, refer to the `requirements.txt` file.

## Usage with Docker
1. Install Docker for your operating system.
2. Downlaod the [Dockerfile](https://github.com/yuriwa/crewai-sheets-ui/blob/main/Dockerfile).
3. From the same folder run:
  `docker build --no-cache -t crewai-image . `
4. Run the Docker container, mapping local port 1234 to container port 1234 and your savedfiles folder  to /home/user/root/savefiles in the container:
  `docker run -it -p 1234:1234 -v ${savefile/path/on/your/computer}:/home/user/root/savefiles -e OPENAI_API_KEY='{YOUR_OPENAI_API KEY}' crewai-image`
5. If you want to use a local LLM instead of OpenAI, host you LLM server on port 1234. You can use LM Studio or any other tool for this.

## Contributing
Contributions to the crewai-sheets-ui project are welcome. Please ensure to follow the project's code of conduct and submit pull requests for any enhancements or bug fixes.

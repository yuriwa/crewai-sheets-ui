# Use a base image with Python 3.10.13
FROM python:3.10.13

# Install updated pip, setuptools, and wheel
RUN pip install --upgrade pip setuptools wheel

# Install crewai and its tools
RUN pip install crewai && pip install 'crewai[tools]'

# Clone crewai-sheet-ui
RUN git clone https://github.com/yuriwa/crewai-sheets-ui.git /home/user/root/crewai-sheets-ui

# Set the working directory in the Docker image

RUN pip install python-dotenv && pip install langchain_openai && pip install pandas && pip install open-interpreter && pip install --upgrade --quiet  duckduckgo-search
#RUN pip install -r /home/user/root/crewai-sheets-ui/requirements.txt

# Create an .env file and add the exports
RUN echo "export VAR1=value1\nexport VAR2=value2" > /home/user/root/crewai-sheets-ui/.env

# Expose port 1234
EXPOSE 1234
WORKDIR /home/user/root/savefiles

CMD if [ -z "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" ]; then \
      echo "Required environment variables are not set." && \
      echo "Run the Docker container, mapping local port 1234 to container port 1234 and the current directory to /home/user in the container:" && \
      echo "docker run -it -p 1234:1234 -v \${local/savefile/path}:/home/user/root/savefiles -e OPENAI_API_KEY='\${YOUR API KEY}' crewai-image"; \
    elif [ ! -d "/home/user/root/savefiles" ]; then \
      echo "The required volume is not mounted." && \
      echo "Run the Docker container, mapping local port 1234 to container port 1234 and the current directory to /home/user in the container:" && \
      echo "docker run -it -p 1234:1234 -v \${local/savefile/path}:/home/user/root/savefiles -e OPENAI_API_KEY='\${YOUR API KEY}' crewai-image"; \
    else \
      python /home/user/root/crewai-sheets-ui/main.py && \
      echo "All set."; \
    fi


# Run the Docker container, mapping local port 1234 to container port 1234 and the current directory to /home/user in the container
#docker run -it -p 1234:1234 -v /{local/savefile/path}}:/home/user/root/savefiles -e OPENAI_API_KEY='sk-111111111111111111' -e SERPER_API_KEY='1111111111' crewai-image python main.py

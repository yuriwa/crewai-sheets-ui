from crewai_tools import (CodeDocsSearchTool,
                            CSVSearchTool, DirectorySearchTool, DOCXSearchTool,
                            DirectoryReadTool, FileReadTool, GithubSearchTool,
                            TXTSearchTool, JSONSearchTool, MDXSearchTool,
                            PDFSearchTool, RagTool, ScrapeElementFromWebsiteTool,
                            ScrapeWebsiteTool, WebsiteSearchTool, XMLSearchTool,
                            YoutubeChannelSearchTool, YoutubeVideoSearchTool)

from langchain.agents.load_tools import load_tools

from langchain_community.tools.ddg_search.tool \
    import DuckDuckGoSearchResults  # Gets search results from Duck Duck Go.

from tools import FileTool  # Create, read, and edit a file line by line
from tools import CLITool  # Interpreter wrapper. Execure any command on the computer


class ToolsMapping:
    code_docs_search_tool = CodeDocsSearchTool()  # A RAG tool optimized for searching through code documentation and related technical documents.
    csv_search_tool = CSVSearchTool()  # A RAG tool designed for searching within CSV files, tailored to handle structured data.
    directory_search_tool = DirectorySearchTool()  # A RAG tool for searching within directories, useful for navigating through file systems.
    docx_search_tool = DOCXSearchTool()  # A RAG tool aimed at searching within DOCX documents, ideal for processing Word files.
    directory_read_tool = DirectoryReadTool()  # Facilitates reading and processing of directory structures and their contents.
    file_read_tool = FileReadTool()  # Enables reading and extracting data from files, supporting various file formats.
    github_search_tool = GithubSearchTool(content_types=['code', 'repo', 'pr', 'issue'])
    # Options: code, repo, pr, issue), 		#A RAG tool for searching within GitHub repositories, useful for code and documentation search.
    # '#seper_dev_tool'		:seper_dev_tool, 			#
    # A specialized tool for development purposes, with specific functionalities under development.
    txt_search_tool = TXTSearchTool()  # A RAG tool focused on searching within text (.txt) files, suitable for unstructured data.
    json_search_tool = JSONSearchTool()  # A RAG tool designed for searching within JSON files, catering to structured data handling.
    mdx_search_tool = MDXSearchTool()  # A RAG tool tailored for searching within Markdown (MDX) files, useful for documentation.
    pdf_search_tool = PDFSearchTool()  # A RAG tool aimed at searching within PDF documents, ideal for processing scanned documents.
    # 'pg_search_tool'		:PGSearchTool()., #pg_search_tool, 			#A RAG tool optimized for searching within PostgreSQL databases, suitable for database queries.
    rag_tool = RagTool()  # A general-purpose RAG tool capable of handling various data sources and types.
    scrape_element_from_website_tool = ScrapeElementFromWebsiteTool()  # Enables scraping specific elements from websites, useful for targeted data extraction.
    scrape_website_tool = ScrapeWebsiteTool()  # Facilitates scraping entire websites, ideal for comprehensive data collection.
    website_searc_tool = WebsiteSearchTool()  # A RAG tool for searching website content, optimized for web data extraction.
    xml_search_tool = XMLSearchTool()  # A RAG tool designed for searching within XML files, suitable for structured data formats.
    youtube_channel_sarch_tool = YoutubeChannelSearchTool()  # A RAG tool for searching within YouTube channels, useful for video content analysis.
    youtube_video_saarch_tool = YoutubeVideoSearchTool()  # A RAG tool aimed at searching within YouTube videos, ideal for video data extraction.
    # langchain------------------------------------------
    human_tools = load_tools(["human"])[0]  # A Tool that allows the Agents to talk to the n .
    search = DuckDuckGoSearchResults()  # Duck duck go Search
    # crewai--sheets-ui
    executor = CLITool.execute_cli_command  # executor_tool,  			#interpreter CLI command
    file_tool = FileTool.manage_file  # Create, read, and edit a file line by line

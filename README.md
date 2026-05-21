# Langraph_codeAgent
AI Agents for coding based on Langraph Platform

Here a simple code agent that creates and executes Python code in a Docker container.
The agent creates the Docker container, executes the code and gives the result in the Gradio UI.

The API-Keys need to be added to the .env file. You can use any LLM, in this example I use gpt-4o-mini. If you want any other, just change the line 34 in the codeAgent.py script.

The agent uses a Docker Image to generate the Docker container. This is done so that no internet connection is required and local LLMs are in use.


Overview
The InfluxDB AI Agent is a powerful tool designed to interact with InfluxDB databases using natural language queries. Built with LangChain, this agent ensures that users can retrieve and query InfluxDB data seamlessly and accurately. Whether you're looking to retrieve data, obtain measurement metadata, or simply list available measurements, this agent provides easy-to-use tools powered by an intelligent AI layer.

The agent uses several tools for querying the InfluxDB database and ensuring query correctness based on natural language input.

Key Features
Natural Language Interface: Allows users to query InfluxDB using human-friendly language.
Accurate Query Validation: Automatically validates and rewrites queries if necessary, ensuring syntactical accuracy and logic correctness.
Multiple Tools:
QueryInfluxDBTool: Executes InfluxDB queries.
InfoInfluxDBTool: Retrieves metadata for specific measurements.
ListInfluxDBTool: Lists all measurements in the database.
LLM-Agnostic: Designed to work with various language models (LLMs) via LangChain.
InfluxDB Compatibility: Supports InfluxQL and Flux queries.
Components
This repository contains the following key files and components:

1. base.py
Contains the base classes and functionality required to interact with the InfluxDB client and LangChain tools.

2. prompt.py
Houses the templates and logic for the natural language query checks. This is used for validating and rewriting queries before executing them.

3. toolkit.py
Implements the core tools (QueryInfluxDBTool, InfoInfluxDBTool, and ListInfluxDBTool) that interact directly with InfluxDB.

4. tools.py
Contains the implementation of additional tools used to handle user queries related to InfluxDB measurements and data retrieval.

Tools Used
The agent utilizes the following tools for interacting with InfluxDB:

QueryInfluxDBTool
A tool designed to run a query against an InfluxDB database and retrieve the data or return an error if the query is incorrect.

Arguments:
query: The query string to run on the InfluxDB instance.
InfoInfluxDBTool
Fetches metadata about specified InfluxDB measurements, including field names and their types.

Arguments:
measurement_names: A comma-separated list of measurement names to retrieve metadata for.
ListInfluxDBTool
Lists all measurements available in the InfluxDB database.

Arguments:
tool_input: Empty string to trigger the listing of measurements.

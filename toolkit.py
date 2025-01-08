from langchain_core.language_models import BaseLanguageModel
from tools import (
    InfoInfluxDBTool,
    ListInfluxDBTool,
    QueryInfluxDBTool,
)
from langchain_core.tools.base import BaseToolkit
from typing import List
from pydantic import Field, ConfigDict
from influxdb import InfluxDBClient


from typing import List, Optional, Any
from pydantic import Field, ConfigDict
from langchain_core.tools.base import BaseToolkit

# Temporarily using Any for BaseLanguageModel and InfluxDBClient
# class InfluxDBToolkit(BaseToolkit):
#     """InfluxDBToolkit for interacting with InfluxDB 1.0 databases."""

#     db: Any = Field(default=None, exclude=True)  # Temporarily use Any for InfluxDBClient
#     llm: Optional[Any] = Field(default=None, exclude=True)  # Temporarily use Any for BaseLanguageModel

#     model_config = ConfigDict(
#         arbitrary_types_allowed=True,
#     )

#     def get_tools(self) -> List:
#         """Get the tools in the toolkit."""
#         from tools import InfoInfluxDBTool, ListInfluxDBTool, QueryInfluxDBTool

#         # List Measurements Tool
#         list_influxdb_tool = ListInfluxDBTool(db=self.db)
        
#         # Info Measurements Tool
#         info_influxdb_tool_description = (
#             "Input to this tool is a comma-separated list of measurement names, output is the "
#             "schema and sample data for those measurements. "
#             "Ensure the measurements exist by calling "
#             f"{list_influxdb_tool.name} first! "
#             "Example Input: measurement1, measurement2, measurement3"
#         )
#         info_influxdb_tool = InfoInfluxDBTool(
#             db=self.db, description=info_influxdb_tool_description
#         )
        
#         # Query Measurements Tool
#         query_influxdb_tool_description = (
#             "Input to this tool is a detailed and correct InfluxQL query, output is a "
#             "result from the database. If the query is not correct, an error message "
#             "will be returned. If an error is returned, rewrite the query, check the "
#             "query, and try again. If you encounter an issue with unknown fields, "
#             f"use {info_influxdb_tool.name} "
#             "to query the correct measurement fields."
#         )
#         query_influxdb_tool = QueryInfluxDBTool(
#             db=self.db, description=query_influxdb_tool_description
#         )

#         # Return list of tools
#         return [
#             query_influxdb_tool,
#             info_influxdb_tool,
#             list_influxdb_tool,
#         ]

#     def get_context(self) -> dict:
#         """Return a simplified context dictionary for use with InfluxDB 1.0."""
#         try:
#             return {"host": self.db._host, "port": self.db._port, "database": self.db._database}
#         except AttributeError:
#             return {"error": "Unable to fetch database context. Ensure the database is connected."}

# InfluxDBToolkit.model_rebuild()

class InfluxDBToolkit(BaseToolkit):
    """InfluxDBToolkit for interacting with InfluxDB 1.0 databases."""

    db: Any = Field(default=None, exclude=True)  # Temporarily use Any for InfluxDBClient
    llm: Optional[Any] = Field(default=None, exclude=True)  # Temporarily use Any for BaseLanguageModel

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    @property
    def database(self) -> str:
        """Fetch the database name from the InfluxDBClient instance."""
        try:
            return self.db._database
        except AttributeError:
            raise ValueError("Database is not properly configured in InfluxDBClient.")

    def get_tools(self) -> List:
        """Get the tools in the toolkit."""
        from tools import InfoInfluxDBTool, ListInfluxDBTool, QueryInfluxDBTool

        # List Measurements Tool
        list_influxdb_tool = ListInfluxDBTool(db=self.db)
        
        # Info Measurements Tool
        info_influxdb_tool_description = (
            "Input to this tool is a comma-separated list of measurement names, output is the "
            "schema and sample data for those measurements. "
            "Ensure the measurements exist by calling "
            f"{list_influxdb_tool.name} first! "
            "Example Input: measurement1, measurement2, measurement3"
        )
        info_influxdb_tool = InfoInfluxDBTool(
            db=self.db, description=info_influxdb_tool_description
        )
        
        # Query Measurements Tool
        query_influxdb_tool_description = (
            "Input to this tool is a detailed and correct InfluxQL query, output is a "
            "result from the database. If the query is not correct, an error message "
            "will be returned. If an error is returned, rewrite the query, check the "
            "query, and try again. If you encounter an issue with unknown fields, "
            f"use {info_influxdb_tool.name} "
            "to query the correct measurement fields."
        )
        query_influxdb_tool = QueryInfluxDBTool(
            db=self.db, description=query_influxdb_tool_description
        )

        # Return list of tools
        return [
            query_influxdb_tool,
            info_influxdb_tool,
            list_influxdb_tool,
        ]

    def get_context(self) -> dict:
        """Return a simplified context dictionary for use with InfluxDB 1.0."""
        try:
            return {"host": self.db._host, "port": self.db._port, "database": self.db._database}
        except AttributeError:
            return {"error": "Unable to fetch database context. Ensure the database is connected."}

InfluxDBToolkit.model_rebuild()

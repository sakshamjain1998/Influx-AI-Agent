from typing import Any, Dict, Optional, Sequence, Type, Union
from influxdb import InfluxDBClient
from pydantic import BaseModel, Field, ConfigDict

from langchain_core.language_models import BaseLanguageModel
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import BaseTool

INFLUX_QUERY_CHECKER = """
{query}
Double check the InfluxDB query above for common mistakes, including:
- Correct syntax for Flux or InfluxQL (whichever is applicable)
- Proper time range specification
- Correct measurement and field references
- Ensuring no unnecessary fields are queried
- Correct filtering logic
- Casting or type adjustments where required

If there are any of the above mistakes, rewrite the query. If there are no mistakes, just reproduce the original query.

Output the final query only.

Query: """

class BaseInfluxDBTool(BaseModel):
    """Base tool for interacting with an InfluxDB database."""

    db: InfluxDBClient = Field(exclude=True)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )


class _QueryInfluxDBToolInput(BaseModel):
    query: str = Field(..., description="A detailed and correct InfluxDB query.")


class QueryInfluxDBTool(BaseInfluxDBTool, BaseTool):
    """Tool for querying an InfluxDB database."""

    name: str = "influx_db_query"
    description: str = (
        "Execute an InfluxDB query against the database and get back the result. "
        "If the query is not correct, an error message will be returned. "
        "If an error is returned, rewrite the query, check the query, and try again."
    )
    args_schema: Type[BaseModel] = _QueryInfluxDBToolInput

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Union[str, Sequence[Dict[str, Any]]]:
        """Execute the query and return results or an error message."""
        try:
            return list(self.db.query(query).get_points())
        except Exception as e:
            return f"Error: {str(e)}"


class _InfoInfluxDBToolInput(BaseModel):
    measurement_names: str = Field(
        ..., description="A comma-separated list of measurement names to get details for. Example: 'cpu, memory'"
    )


class InfoInfluxDBTool(BaseInfluxDBTool, BaseTool):
    """Tool for getting metadata about InfluxDB measurements."""

    name: str = "influx_db_measurement_info"
    description: str = "Get the metadata for the specified InfluxDB measurements."
    args_schema: Type[BaseModel] = _InfoInfluxDBToolInput

    def _run(
        self,
        measurement_names: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Get metadata for measurements in a comma-separated list."""
        measurements = [m.strip() for m in measurement_names.split(",")]
        try:
            metadata = {}
            for measurement in measurements:
                field_keys = self.db.query(f"SHOW FIELD KEYS FROM {measurement}")
                metadata[measurement] = {
                    "fields": [item["fieldKey"] for item in field_keys.get_points()]
                }
            return str(metadata)
        except Exception as e:
            return f"Error: {str(e)}"


class _ListInfluxDBToolInput(BaseModel):
    tool_input: str = Field("", description="An empty string")


class ListInfluxDBTool(BaseInfluxDBTool, BaseTool):
    """Tool for listing InfluxDB measurements."""

    name: str = "influx_db_list_measurements"
    description: str = "Input is an empty string, output is a comma-separated list of measurements in the database."
    args_schema: Type[BaseModel] = _ListInfluxDBToolInput

    def _run(
        self,
        tool_input: str = "",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Get a comma-separated list of measurement names."""
        try:
            result = self.db.query("SHOW MEASUREMENTS")
            measurements = [item["name"] for item in result.get_points()]
            return ", ".join(measurements)
        except Exception as e:
            return f"Error: {str(e)}"





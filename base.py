from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Sequence,
    Union,
    cast,
)

from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.prompts import BasePromptTemplate, PromptTemplate
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)

from prompt import (
    INFLUX_FUNCTIONS_SUFFIX,
    INFLUX_PREFIX,
    INFLUX_SUFFIX,
)
from toolkit import InfluxDBToolkit

if TYPE_CHECKING:
    from langchain.agents.agent import AgentExecutor
    from langchain.agents.agent_types import AgentType
    from langchain_core.callbacks import BaseCallbackManager
    from langchain_core.language_models import BaseLanguageModel
    from langchain_core.tools import BaseTool


def create_influx_agent(
    llm: BaseLanguageModel,
    toolkit: Optional[InfluxDBToolkit] = None,
    agent_type: Optional[
        Union[AgentType, Literal["openai-tools", "tool-calling"]]
    ] = None,
    callback_manager: Optional[BaseCallbackManager] = None,
    prefix: Optional[str] = None,
    suffix: Optional[str] = None,
    format_instructions: Optional[str] = None,
    input_variables: Optional[List[str]] = None,
    top_k: int = 10,
    max_iterations: Optional[int] = 15,
    max_execution_time: Optional[float] = None,
    early_stopping_method: str = "force",
    verbose: bool = False,
    agent_executor_kwargs: Optional[Dict[str, Any]] = None,
    extra_tools: Sequence[BaseTool] = (),
    **kwargs: Any,
) -> AgentExecutor:
    """Construct an InfluxDB agent from an LLM and toolkit.

    Args:
        llm: Language model to use for the agent. If agent_type is "tool-calling" then
            llm is expected to support tool calling.
        toolkit: InfluxDBToolkit for the agent to use.
        agent_type: One of "tool-calling", "openai-tools", "openai-functions", or
            "zero-shot-react-description". Defaults to "zero-shot-react-description".
        callback_manager: DEPRECATED. Pass "callbacks" key into 'agent_executor_kwargs'
            instead to pass constructor callbacks to AgentExecutor.
        prefix: Prompt prefix string. Must contain variables "top_k" and "database".
        suffix: Prompt suffix string. Default depends on agent type.
        format_instructions: Formatting instructions to pass to
            ZeroShotAgent.create_prompt() when 'agent_type' is
            "zero-shot-react-description". Otherwise ignored.
        input_variables: DEPRECATED.
        top_k: Number of rows to query for by default.
        max_iterations: Passed to AgentExecutor init.
        max_execution_time: Passed to AgentExecutor init.
        early_stopping_method: Passed to AgentExecutor init.
        verbose: AgentExecutor verbosity.
        agent_executor_kwargs: Arbitrary additional AgentExecutor args.
        extra_tools: Additional tools to give to agent on top of the ones that come with
            InfluxDBToolkit.
        **kwargs: Arbitrary additional Agent args.

    Returns:
        An AgentExecutor with the specified agent_type agent.

    Example:

        .. code-block:: python

            from langchain_openai import ChatOpenAI
            from influxdb_toolkit import create_influx_agent

            llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
            toolkit = InfluxDBToolkit(database_uri="http://localhost:8086", token="my-token")
            agent_executor = create_influx_agent(llm, toolkit=toolkit, agent_type="tool-calling", verbose=True)

    """  # noqa: E501
    from langchain.agents import (
        create_openai_functions_agent,
        create_openai_tools_agent,
        create_react_agent,
        create_tool_calling_agent,
    )
    from langchain.agents.agent import AgentExecutor, RunnableAgent, RunnableMultiActionAgent
    from langchain.agents.agent_types import AgentType

    if toolkit is None:
        raise ValueError("Toolkit must be provided.")

    agent_type = agent_type or AgentType.ZERO_SHOT_REACT_DESCRIPTION
    tools = toolkit.get_tools() + list(extra_tools)
    if prefix is None:
        prefix = INFLUX_PREFIX
    prefix = prefix.format(database=toolkit.database, top_k=top_k)

    if agent_type == AgentType.ZERO_SHOT_REACT_DESCRIPTION:
        if format_instructions is None:
            format_instructions = "Please ensure output adheres to InfluxDB query structure."
        template = "\n\n".join([
            prefix,
            "{tools}",
            format_instructions,
            suffix or INFLUX_SUFFIX,
        ])
        prompt = PromptTemplate.from_template(template)
        agent = RunnableAgent(
            runnable=create_react_agent(llm, tools, prompt),
            input_keys_arg=["input"],
            return_keys_arg=["output"],
            **kwargs,
        )

    elif agent_type == "tool-calling":
        if not suffix:
            suffix = INFLUX_FUNCTIONS_SUFFIX
        messages = [
            SystemMessage(content=cast(str, prefix)),
            HumanMessagePromptTemplate.from_template("{input}"),
            AIMessage(content=suffix),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
        prompt = ChatPromptTemplate.from_messages(messages)
        runnable = create_tool_calling_agent(llm, tools, prompt)  # type: ignore
        agent = RunnableMultiActionAgent(
            runnable=runnable,
            input_keys_arg=["input"],
            return_keys_arg=["output"],
            **kwargs,
        )

    else:
        raise ValueError(
            f"Agent type {agent_type} not supported. Must be one of "
            "'tool-calling', 'zero-shot-react-description'."
        )

    return AgentExecutor(
        name="InfluxDB Agent Executor",
        agent=agent,
        tools=tools,
        callback_manager=callback_manager,
        verbose=verbose,
        max_iterations=max_iterations,
        max_execution_time=max_execution_time,
        early_stopping_method=early_stopping_method,
        **(agent_executor_kwargs or {}),
    )
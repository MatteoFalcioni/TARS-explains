from langgraph.types import Command
from typing_extensions import Annotated, Literal
from TARS.state import TARSState
from langgraph.prebuilt import create_react_agent, InjectedState
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, START
from dotenv import load_dotenv

from TARS.prompt import TARS_PROMPT
from TARS.tools import write_equation, set_humor, get_humor


load_dotenv()

tars_llm = ChatOpenAI(model="gpt-4.1")

TARS_agent = create_react_agent(
        model=tars_llm,
        tools=[write_equation, set_humor, get_humor],
        prompt=TARS_PROMPT,
        name="TARS_agent",
        state_schema=TARSState,
    )

def TARS_node(state: Annotated[TARSState, InjectedState]
) -> Command[Literal["__end__"]]:
    
    result = TARS_agent.invoke(state)
    return Command(update={**result}, goto="__end__")


def make_graph(checkpointer=None):
    builder = StateGraph(TARSState)
    builder.add_node("TARS_agent", TARS_node)
    builder.add_edge(START, "TARS_agent")
    return builder.compile(checkpointer=checkpointer)
    
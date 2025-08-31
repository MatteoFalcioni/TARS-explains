from langgraph.types import Command
from typing_extensions import Annotated, Literal
from state import TARSState
from langgraph.prebuilt import create_react_agent, InjectedState
from langchain_openai import ChatOpenAI
from prompts import TARS_PROMPT
from tools import write_equations, set_humor, get_humor
from langgraph.graph import StateGraph, START


tars_llm = ChatOpenAI("gpt:4o", temperature=0.5)

TARS_agent = create_react_agent(
        model=tars_llm,
        tools=[write_equations, set_humor, get_humor],
        prompt=TARS_PROMPT,
        name="TARS_agent",
        state_schema=TARSState,
    )

def TARS_node(state: Annotated[TARSState, InjectedState]
) -> Command[Literal["__end__"]]:
    
    result = TARS_agent.invoke(state)
    return Command(update={**result}, goto="__end__")


def make_graph():
    builder = StateGraph(TARSState)
    builder.add_node("TARS_agent", TARS_node)
    builder.add_edge(START, "TARS_agent")
    return builder.compile()    #checkpointer=checkpointer add short term memory
    
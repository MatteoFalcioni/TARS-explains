from langgraph.types import Command
from langchain_core.tools import InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
import os
from typing_extensions import Annotated
import uuid

from state import TARSState

EQUATIONS_DIR = "equations"
os.makedirs(EQUATIONS_DIR, exist_ok=True)

@tool
def write_equations(
    equation: Annotated[str, "Markdown content of ONE equation."],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """
    Write an equation in Markdown to the filesystem.
    Start the text file with the equation number as title, like # eq. 1
    Returns the saved path and appends it to state['equations'].
    """
    
    short = str(uuid.uuid4())[:8]
    eq_path = f"{EQUATIONS_DIR}/equation_{short}.md"

    content = equation

    with open(eq_path, "w") as f:
        f.write(content)

    new_entry = {"filename": eq_path, "content": content}

    return Command(
        update={
            "messages": [ToolMessage(content=f"Equation written to {eq_path}", tool_call_id=tool_call_id)],
            "equations": new_entry,   # not Path, not nested
        }
    )

@tool 
def set_humor(value : Annotated[int, "The humor value to set"],
              tool_call_id : Annotated[str, InjectedToolCallId]) -> Command:
    """
    Set the humor value as an integer value from 0 to 100, representing a percentage of humor
    """
    return Command(
        update={
            "messages" : [ToolMessage(content=f"Humor set to {value}%", tool_call_id=tool_call_id)],
            "humor": value
        }
    )

@tool
def get_humor(state: Annotated[TARSState, InjectedState], tool_call_id : Annotated[str, InjectedToolCallId]) -> Command:
    """
    Get the current humor value: it will be an integer value from 0 to 100, representing a percentage of humor
    """

    current_humor = state.get('humor', 'not set')

    if current_humor == 'not set':
        print("Humor is not set!")

    return Command(
        update={
            "messages" : [ToolMessage(content=f"Humor is at {current_humor}%", tool_call_id=tool_call_id)]
        }
    )







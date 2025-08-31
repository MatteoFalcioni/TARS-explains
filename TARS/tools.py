from langgraph.types import Command
from langchain_core.tools import InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from pathlib import Path
from typing_extensions import Annotated
import uuid

from state import TARSState

EQUATIONS_DIR = Path("equations")

@tool
def write_equations(
    equations: Annotated[str, "Markdown content of ONE equation (use $$ LaTeX $$)."],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """
    Write ONE equation in Markdown to the filesystem.
    Start the text file with the equation number as title, like # eq. 1
    Returns the saved path and appends it to state['equations'].
    """
    EQUATIONS_DIR.mkdir(parents=True, exist_ok=True)
    short = str(uuid.uuid4())[:8]
    eq_path = EQUATIONS_DIR / f"equation_{short}.md"

    eq_path.write_text(equations)

    return Command(
        update={
            "messages" : [ToolMessage(content=f"Equations written to {eq_path}", tool_call_id=tool_call_id)],
            "equations": eq_path
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

    current_humor = state.get('humor', None)

    if not current_humor:
        raise ValueError("Humor is not set")

    return Command(
        update={
            "messages" : [ToolMessage(content=f"Humor is at {current_humor}%", tool_call_id=tool_call_id)]
        }
    )







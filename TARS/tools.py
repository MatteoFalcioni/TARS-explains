from langgraph.types import Command
from langchain_core.tools import InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from pathlib import Path
from typing_extensions import Annotated
import uuid

from state import TARSState

@tool 
def write_equations(equations : Annotated[str, "The equations to write down, in markdown format"],
                    tool_call_id : Annotated[int, InjectedToolCallId]) -> Command:
    """
    Write equations in markdown format to file system
    """
    # unique eqs. path for each call
    eqs_path = f"equations/equations_{uuid.uuid4()[:8]}.md"
    Path(eqs_path).mkdir(parents=True, exist_ok=True)
    eqs_path.write_text(equations)

    return Command(
        update={
            "messages" : [ToolMessage(content=f"Equations written to {eqs_path}", tool_call_id=tool_call_id)],
            "equations": eqs_path
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
def get_humor(state: Annotated[TARSState, InjectedState]) -> Command:
    """
    Get the current humor value: it will be an integer value from 0 to 100, representing a percentage of humor
    """

    current_humor = state.get('humor', None)

    return Command(
        update={
            "messages" : [ToolMessage(content=f"Humor is {current_humor}%")]
        }
    )







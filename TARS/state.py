from typing import List, Union
from typing_extensions import Annotated, Dict
from langgraph.prebuilt.chat_agent_executor import AgentState

def add_file(current_files: Union[Dict[str, str], None] = None, 
             new_file: Union[Dict[str, str], None] = None
)-> Dict[str, str]:
    """
    Reducer to add a file to the state `files` list
    """

    left = current_files or {}
    right = new_file or {}

    return {**left, **right}

def update_humor(current_value: Union[int, None] = None, 
                 new_value: Union[int, None] = None
)-> int:
    if not current_value:
        current_value = 90
    if not new_value:
        return current_value
    return new_value

class TARSState(AgentState):
    humor: Annotated[int, update_humor] 
    equations: Annotated[Dict[str, str], add_file]

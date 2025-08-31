from typing import List, Union
from typing_extensions import Annotated
from langgraph.prebuilt.chat_agent_executor import AgentState

def add_file(current_files: Union[List[str], None] = None, 
             new_file: Union[str, None] = None
)-> List:
    """
    Reducer to add a file to the state `files` list
    """

    if not current_files:
        current_files = []
    if not new_file:
        return current_files

    if new_file in current_files:   # already in state, skip
        return current_files
    
    else: # save under full sandbox path
        current_files.append(new_file)
    return current_files

def update_humor(current_value: Union[int, None] = None, 
                 new_value: Union[int, None] = None
)-> int:
    if not current_value:
        current_value = 90
    if not new_value:
        return current_value
    return new_value

class TARSState(AgentState):
    """
    The state of the agent.
    """
    humor: Annotated[int, update_humor]
    equations: Annotated[List[str], add_file]  
    

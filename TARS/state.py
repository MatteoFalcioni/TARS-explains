from typing import List, Union
from typing_extensions import Annotated, Dict
from langgraph.graph import MessagesState

def add_file(current_files: Union[Dict[str, str], None] = None, 
             new_file: Union[Dict[str, str], None] = None
)-> Dict[str, str]:
    """
    Reducer to add a file to the state `files` list
    """

    if not current_files:
        current_files = {}
    if not new_file:
        return current_files

    if new_file['filename'] in current_files.keys():   # already in state, skip
        return current_files
    
    else: # save under full sandbox path
        current_files[new_file['filename']] = new_file['content']
    return current_files

def update_humor(current_value: Union[int, None] = None, 
                 new_value: Union[int, None] = None
)-> int:
    if not current_value:
        current_value = 90
    if not new_value:
        return current_value
    return new_value

class TARSState(MessagesState):
    humor: Annotated[int, update_humor] 
    equations: Annotated[Dict[str, str], add_file]
    remaining_steps : int

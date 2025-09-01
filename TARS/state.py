from typing import List, Union, Optional
from typing_extensions import Annotated, Dict
from langgraph.prebuilt.chat_agent_executor import AgentState

def add_file(current_files: Union[Dict[str, str], None] = None, 
             new_file: Union[Dict[str, str], None] = None
)-> Dict[str, str]:
    """
    Reducer to add a file to the state `equations` dictionary
    """

    left = current_files or {}
    right = new_file or {}

    return {**left, **right}


def add_to_list(current_list: Optional[List[str]] = None,
                new_item: Optional[str] = None) -> List[str]:
    """
    Reducer to add an item to the state `equations` list
    """
    left = current_list or []
    if new_item is None:
        return left[:]   # copia immutabile
    if new_item in left:
        return left[:]   # già presente, restituisco copia
    return left + [new_item]   # nuova lista, aggiunto in coda


def update_humor(current_value: Union[int, None] = None, 
                 new_value: Union[int, None] = None
)-> int:
    if not current_value:
        current_value = 90
    if not new_value:
        return current_value
    return new_value

'''class TARSState(AgentState):
    humor: Annotated[int, update_humor] 
    equations: Annotated[Dict[str, str], add_file]'''

class TARSState(AgentState):
    humor: Annotated[int, update_humor] 
    equations: Annotated[List[str], add_to_list]

from graph import make_graph
from dotenv import load_dotenv
import os
import uuid

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

if __name__ == "__main__":

    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY not found in environment!")
    
    checkpointer = InMemorySaver()
    
    graph = make_graph(checkpointer=checkpointer)
    
    convo_id = str(uuid.uuid4())[:8]

    print("=== Type /bye to exit. ===\n")

    usr_msg = ""

    while True:

        usr_msg = input("User: ")

        if "/bye" in usr_msg.lower():
            break

        result = graph.invoke(
            {"messages": [{"role": "user", "content": usr_msg}]},
            {"configurable": {"thread_id": f"{convo_id}"}, "recursion_limit" : 45},
        )

        ai_message = result["messages"][-1].content

        print(f'\nTARS: {ai_message}\n')


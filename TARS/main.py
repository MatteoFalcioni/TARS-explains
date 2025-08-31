from graph import make_graph
from dotenv import load_dotenv
import os

if __name__ == "__main__":

    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY not found in environment!")
    
    graph = make_graph()

    print("=== Type /bye to exit. ===\n")

    usr_msg = ""

    while True:

        usr_msg = input("User: ")

        if "/bye" in usr_msg.lower():
            break

        result = graph.invoke(
            {"messages": [{"role": "user", "content": usr_msg}]},
            {"configurable": {"thread_id": "1"}, "recursion_limit" : 25},
        )

        ai_message = result["messages"][-1].content

        print(f'\nTARS: {ai_message}\n')
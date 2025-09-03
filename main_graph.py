from TARS.graph import make_graph   
from langgraph.checkpoint.memory import InMemorySaver
import uuid
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

from TARS.state import TARSState
from T2S_S2T.speech_to_text import record_audio_until_stop
from T2S_S2T.text_2_speech1 import play_audio

if __name__ == "__main__":

    load_keys = load_dotenv(dotenv_path="main.env", verbose=True)
    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY not found in environment!")
    if not os.getenv("XI_API_KEY"):
        raise EnvironmentError("ELEVENLABS_API_KEY not found in environment!")

    # memory
    checkpointer = InMemorySaver()
    
    # Define subgraph
    TARS_subgraph = make_graph()

    # Define parent graph
    builder = StateGraph(TARSState)

    # Add sub graph directly as a node
    builder.add_node("audio_input", record_audio_until_stop)
    builder.add_node("TARS", TARS_subgraph)
    builder.add_node("audio_output", play_audio)
    builder.add_edge(START, "audio_input")
    builder.add_edge("audio_input", "TARS")
    builder.add_edge("TARS","audio_output")
    builder.add_edge("audio_output", END)
    graph = builder.compile(checkpointer=checkpointer)

    png_bytes = graph.get_graph(xray=1).draw_mermaid_png()

    # Save to file
    with open("./tars_graph.png", "wb") as f:
        f.write(png_bytes)

    # Set user ID for storing memories
    thread_id = str(uuid.uuid4())[:8]
    config = {"configurable": {"user_id": "Test-Audio-UX", "thread_id": thread_id}, "recursion_limit": 50}

    print("Initializing TARS...\n")

    while True:

        print("\n------ Type /bye to exit. Press any other key to record. ------\n")
        usr_msg = input("")

        if "/bye" in usr_msg.lower():
            break

        # Kick off the graph, which will record user input until the user presses Enter
        for chunk in graph.stream({"messages":HumanMessage(content="Follow the user's instructions:")}, stream_mode="values", config=config):
            chunk["messages"][-1].pretty_print()
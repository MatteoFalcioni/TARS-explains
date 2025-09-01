from TARS.graph import make_graph   
from langgraph.checkpoint.memory import InMemorySaver
import uuid
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage

from TARS.state import TARSState
from T2S_S2T.text_2_speech import record_audio_until_stop
from T2S_S2T.speech_2_text import play_audio

if __name__ == "__main__":

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
    builder.add_edge("audio_output",END)
    graph = builder.compile()

    png_bytes = graph.get_graph(xray=1).draw_mermaid_png()

    # Save to file
    with open("./tars_graph.png", "wb") as f:
        f.write(png_bytes)

    # Set user ID for storing memories
    thread_id = str(uuid.uuid4())[:8]
    config = {"configurable": {"user_id": "Test-Audio-UX", "thread_id": thread_id}}

    # Kick off the graph, which will record user input until the user presses Enter
    for chunk in graph.stream({"messages":HumanMessage(content="Follow the user's instructions:")}, stream_mode="values", config=config):
        chunk["messages"][-1].pretty_print()
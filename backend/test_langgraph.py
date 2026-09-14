from langgraph.graph import StateGraph, END
from typing import TypedDict

class S(TypedDict):
    x: str

g = StateGraph(S)
print("StateGraph OK")

def node1(state):
    return {"x": "hello"}

g.add_node("node1", node1)
g.set_entry_point("node1")
g.add_edge("node1", END)
app = g.compile()
result = app.invoke({"x": ""})
print(f"Result: {result}")
print("LangGraph fully functional!")

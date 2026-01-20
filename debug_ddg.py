from agent import agent
from agno.tools.duckduckgo import DuckDuckGoTools

print("--- DEBUGGING DUCKDUCKGO OUTPUT ---")
ddg = DuckDuckGoTools()
# Simulate a search call properties if possible, or just run the agent again and capture output
# Easier to just run agent and capture the tool event output
try:
    stream = agent.run("Search for 'DeepSeek features'", stream=True, stream_events=True)
    for chunk in stream:
        if hasattr(chunk, "event") and "ToolCallCompleted" in chunk.event:
            print("\n[TOOL OUTPUT FOUND]:")
            if hasattr(chunk, "tool_output"):
                 print(chunk.tool_output)
            # creating a dict to see full structure relative to tool output
            if hasattr(chunk, "to_dict"):
                 print(chunk.to_dict())
except Exception as e:
    print(f"Error: {e}")

from agent import agent
from pprint import pprint

print("--- DEBUGGING TOOL EVENTS ---")
# Force a tool call (DuckDuckGo or YFinance)
# We ask something that requires a tool, like "What is the stock price of NVDA?"
try:
    # Try passing stream_events=True to run()
    stream = agent.run("What is the stock price of NVDA?", stream=True, stream_events=True)
    for chunk in stream:
        print("\n[CHUNK RAW]:", type(chunk))
        if hasattr(chunk, "to_dict"):
            data = chunk.to_dict()
            print("[CHUNK DICT]:")
            pprint(data)
        elif hasattr(chunk, '__dict__'):
             print("[CHUNK __DICT__]:")
             pprint(chunk.__dict__)
        else:
            print("[CHUNK STR]:", str(chunk))
except Exception as e:
    print(f"Error: {e}")
print("--- END DEBUG ---")

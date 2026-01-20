from agent import agent
from pprint import pprint
import time

print("--- Starting Event Stream Debug (File Tool Test) ---")
# File tool is usually more obedient
stream = agent.run("Create a file named 'test_debug.txt' with content 'Hello World'", stream=True)

for chunk in stream:
    # Check for direct event attributes first
    if hasattr(chunk, "event"):
        event_name = chunk.event
        if "Tool" in str(event_name):
            print(f"!!! FOUND TOOL EVENT: {chunk}")
            if hasattr(chunk, "to_dict"):
                pprint(chunk.to_dict())
        else:
            pass # Ignore regular content for now
    else:
        # Fallback check
        if "Tool" in str(type(chunk)):
             print(f"!!! FOUND TOOL EVENT BY TYPE: {chunk}")

print("--- End of Stream ---")

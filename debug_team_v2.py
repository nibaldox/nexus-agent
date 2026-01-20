
from agents.manager import manager
import json
from dataclasses import asdict, is_dataclass
import sys

def test_team_stream():
    print("DEBUG_START")
    try:
        # Message to trigger delegation
        message = "What is the stock price of Apple?"
        # Run Manager
        stream = manager.run(message, stream=True, stream_events=True)
        
        for i, chunk in enumerate(stream):
            data = None
            if hasattr(chunk, "to_dict"):
                data = chunk.to_dict()
            elif is_dataclass(chunk):
                data = asdict(chunk)
            
            if data:
                # Print the event type clearly
                event_type = data.get('event')
                print(f"EVENT_TYPE: {event_type}")
                
                # Check for agent identifiers
                if "agent_name" in data or "team_name" in data:
                    print(f"  --> AGENT/TEAM: {data.get('agent_name') or data.get('team_name')}")
                
                if "content" in data:
                    print(f"  --> CONTENT PREVIEW: {str(data.get('content'))[:50]}...")
            
            if i > 50:
                print("... limiting output to 50 chunks ...")
                break
                
    except Exception as e:
        print(f"ERROR: {e}")
    print("DEBUG_END")

if __name__ == "__main__":
    test_team_stream()

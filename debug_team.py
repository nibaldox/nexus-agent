
from agents.manager import manager
import json
from dataclasses import asdict, is_dataclass

def test_team_stream():
    print("Starting Team Stream Test...")
    message = "Who are you?"
    try:
        # Mimic api.py call
        stream = manager.run(message, stream=True, stream_events=True)
        
        print("Stream object:", type(stream))
        
        count = 0
        for chunk in stream:
            count += 1
            print(f"--- Chunk {count} ---")
            print(f"Type: {type(chunk)}")
            # print(f"Raw: {chunk}")
            
            data = None
            if hasattr(chunk, "to_dict"):
                data = chunk.to_dict()
            elif is_dataclass(chunk):
                data = asdict(chunk)
            else:
                data = {"event": "Unknown", "content": str(chunk)}
            
            print(f"Serialized keys: {list(data.keys()) if data else 'None'}")
            if count > 5:
                print("... limiting output ...")
                break
                
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_team_stream()

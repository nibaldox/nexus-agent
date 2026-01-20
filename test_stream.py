from agent import agent

print("Testing stream...")
try:
    # Force tool use
    gen = agent.run("Busca el precio de Apple en YFinance", stream=True)
    for chunk in gen:
        event_type = getattr(chunk, "event", "Unknown")
        print(f"Event: {event_type} | Type: {type(chunk).__name__}")
        if hasattr(chunk, "content") and chunk.content:
            print(f"  > Content: {chunk.content[:50]}...")
        if hasattr(chunk, "reasoning_content") and chunk.reasoning_content:
             print(f"  > Reasoning: {chunk.reasoning_content[:50]}...")
        if hasattr(chunk, "tools") and chunk.tools:
             print(f"  > Tools: {chunk.tools}")
except Exception as e:
    print(f"Error: {e}")

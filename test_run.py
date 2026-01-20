from agent import agent
import inspect

print("Methods of agent:")
print([m for m in dir(agent) if not m.startswith("_")])

try:
    print("\nIntrospection of 'run' method:")
    if hasattr(agent, "run"):
        print(inspect.signature(agent.run))
    else:
        print("'run' method not found.")
except Exception as e:
    print(f"Error inspecting run: {e}")

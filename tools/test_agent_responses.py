import importlib
import inspect

agents_info = [
    ('researcher','agents.researcher','researcher'),
    ('analyst','agents.analyst','analyst'),
    ('librarian','agents.librarian','librarian'),
    ('visualizer','agents.visualizer','visualizer'),
    ('manager','agents.manager','manager')
]

prompt = 'Por favor responde en una frase: di tu nombre y rol.'

print('Starting agent response tests...')
for label, module_name, instance_name in agents_info:
    print('\n' + '='*60)
    print(f'Testing {label} ({module_name}.{instance_name})')
    try:
        mod = importlib.import_module(module_name)
        inst = getattr(mod, instance_name)
    except Exception as e:
        print('IMPORT ERROR:', e)
        continue

    # Find a callable method to produce a quick response
    methods_to_try = ['print_response','respond_sync','respond','ask','run','call']
    called = False
    for mname in methods_to_try:
        if hasattr(inst, mname):
            method = getattr(inst, mname)
            try:
                sig = inspect.signature(method)
                args = []
                kwargs = {}
                # try to provide (prompt) or (prompt, stream=False)
                if len(sig.parameters) == 0:
                    print(f'Calling {mname}()')
                    res = method()
                else:
                    # prefer stream=False if available
                    if 'stream' in sig.parameters:
                        print(f'Calling {mname}(prompt, stream=False)')
                        res = method(prompt, stream=False)
                    else:
                        print(f'Calling {mname}(prompt)')
                        res = method(prompt)
                print('CALL OK; returned:', repr(res))
                called = True
                break
            except Exception as e:
                print(f'Calling {mname} raised:', e)
                # continue trying other methods
    if not called:
        print('No callable response method succeeded for this agent; skipping.')

print('\nAll tests finished.')

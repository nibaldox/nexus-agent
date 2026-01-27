from api import extract_from_run_string


def test_extract_from_run_string_messages_and_input():
    raw = """
    {
        "messages": [{"role": "assistant", "content": "respuesta"}],
        "input_content": "pregunta"
    }
    """
    items = extract_from_run_string(raw)
    contents = [item["content"] for item in items]
    assert "respuesta" in contents
    assert "pregunta" in contents


def test_extract_from_run_string_content_fallback():
    raw = '{"content": "solo contenido"}'
    items = extract_from_run_string(raw)
    assert any(item["content"] == "solo contenido" for item in items)

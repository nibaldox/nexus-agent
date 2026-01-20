from agno.tools.websearch import WebSearchTools

if __name__ == '__main__':
    ws = WebSearchTools(backend='auto', timeout=8)
    queries = [
        'copper price 2024',
        'copper price 2024 monthly average',
        'site:investing.com copper historical data 2024'
    ]
    for q in queries:
        print('\n--- QUERY:', q)
        try:
            res = ws.web_search(q, max_results=5)
            print('RESULT SAMPLE:', res[:1000])
        except Exception as e:
            print('ERROR:', e)

import os
from dotenv import load_dotenv
load_dotenv()
try:
    import google.generativeai as genai
except Exception as e:
    print('GENAI_IMPORT_ERROR', e)
    raise

api_key = os.getenv('GEMINI_API_KEY')
print('Using GEMINI_API_KEY set:', bool(api_key))
if not api_key:
    print('No GEMINI_API_KEY found. Set it in environment or .env and retry.')
else:
    try:
        genai.configure(api_key=api_key)
        models = genai.list_models()
        print('Available models:')
        for m in models:
            # model objects sometimes are simple dicts or objects
            try:
                name = getattr(m, 'name', None) or m.get('name') if isinstance(m, dict) else str(m)
            except Exception:
                name = str(m)
            print('-', name)
    except Exception as e:
        print('ERROR_LIST_MODELS:', e)
        raise

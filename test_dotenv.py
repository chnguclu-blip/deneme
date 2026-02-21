try:
    from dotenv import load_dotenv
    print("SUCCESS: dotenv imported")
except ImportError as e:
    print(f"FAILURE: {e}")

import os
from dotenv import load_dotenv

def main():
    load_dotenv()
    print("--- AutoProcure AI Initialized ---")
    print(f"Caspian Key Loaded: {os.getenv('CASPIAN_API_KEY') is not None}")

if __name__ == "__main__":
    main()

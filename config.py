import os
from dotenv import load_dotenv
import google.genai as genai
from tavily import TavilyClient
import serpapi

# Load Environment Variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

GEMINI_MODEL = 'gemini-2.5-flash'
DEFAULT_REST_NAME = "Matsui"
DEFAULT_ZIP = "90717"

if not GOOGLE_API_KEY or not TAVILY_API_KEY or not SERPAPI_API_KEY:
    raise RuntimeError("Missing Keys! Add GOOGLE_API_KEY, TAVILY_API_KEY, and SERPAPI_API_KEY to .env")

tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
serpapi_client = serpapi.Client(api_key=SERPAPI_API_KEY)
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
serpapi_client = serpapi.Client(api_key=SERPAPI_API_KEY)

import os
import supabase
from dotenv import load_dotenv

#we are loading the env variable and connecting to db
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("the supabase credentials are missing, please Check the content of .env file")

# Initialize Client
supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

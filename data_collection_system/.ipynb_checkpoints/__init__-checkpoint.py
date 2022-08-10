from redis import Redis
from dotenv import load_dotenv
import os
import sys
import pathlib

try:
    """
    load the environment variables from .env file
    """
    
    load_dotenv()
    
    DB_HOST = os.getenv("SERVER_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_DATABASE = os.getenv("DB_DATABASE")
    #DB_USER = os.getenv("DB_USER")
    #DB_PASSWD = os.getenv("DB_PASSWD")

    CACHE_HOST = os.getenv("SERVER_HOST")
    CACHE_PORT = os.getenv("CACHE_PORT") 
    CACHE_DATABASE = os.getenv("CACHE_DATABASE") 
    CACHE_PASSWORD = os.getenv("CACHE_PASSWORD")
    
    ScraperAPI_API_KEY = os.getenv("ScraperAPI_API_KEY")
    ScraperAPI_proxy = {
      "http": f"""http://scraperapi:{ScraperAPI_API_KEY}@proxy-server.scraperapi.com:8001"""
    }
    """
    spam url, farm content, fake news sites 
    """
    BLOCK_RULE = {  # RE: regular expression, URL: url of website
        #"sns-content-farms.txt" : "RE",
        #"scam-sites.txt" : "RE%URL",
        #"content-farms.txt" : "RE%URL",
        #"nearly-content-farms.txt" : "URL",
        #"fake-news.txt" : "URL",
        "custom.txt" : "URL",
        "non_block.txt" : "NON",
        #"blog.txt" : "NON",
    }
    BLOCK_DIR = f"""{str(pathlib.Path(__file__).resolve().parent)}/file/blocklist"""

except Exception as error:
    raise error
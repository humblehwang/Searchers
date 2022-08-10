import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.resolve()))
import os
import json
from data_collection_system import BLOCK_RULE, BLOCK_DIR
from data_collection_system.tools.utils import get_cache_connection
from data_collection_system.tools import log

logger = log.create_logger()

def set_block_rule():
    """
    utility : set the rule of block
    """
    try:
        cache_connection = get_cache_connection()
        cache_connection.delete("BLOCK_RULE")
        cache_connection.hmset("BLOCK_RULE",BLOCK_RULE)
        logger.info("setting blcok rule successfully")
        return True
    except Exception as error:
        logger.error(f"""set_block_rule with {error}""")
        return False
           
def get_block_rule():
    try:
        cache_connection = get_cache_connection()
        return cache_connection.hgetall("BLOCK_RULE")
    except Exception as error:
        logger.error(f"""get_block_rule with {error}""")
        return False

def get_block_url_set():
    try:
        cache_connection = get_cache_connection() 
        return cache_connection.smembers("BLOCK_URL_SET")
    except Exception as error:
        logger.error(f"""get_block_url_set with {error}""")
        return False
    
def get_non_block_url_set():
    try:
        cache_connection = get_cache_connection() 
        return cache_connection.smembers("NON_BLOCK_URL_SET")
    except Exception as error:
        logger.error(f"""get_non_block_url_set with {error}""")
        return False    
    
def get_block_re_set():
    try:
        cache_connection = get_cache_connection() 
        return cache_connection.smembers("BLOCK_RE_SET")
    except Exception as error:
        logger.error(f"""get_block_re_set with {error}""")
        return False
    
def set_block_set():
    try:
        cache_connection = get_cache_connection()
        cache_connection.delete("BLOCK_URL_SET")
        cache_connection.delete("NON_BLOCK_URL_SET")
        cache_connection.delete("BLOCK_RE_SET")
        file_list = os.listdir(BLOCK_DIR)
        for file_name in file_list:
            if '.txt' not in file_name or file_name not in BLOCK_RULE:
                continue

            file_txt = open(f"""{BLOCK_DIR}/{file_name}""")
            data = file_txt.readlines()
            file_txt.close()
            
            if BLOCK_RULE[file_name] == "NON":
                for d in data:
                    cache_connection.sadd("NON_BLOCK_URL_SET", d.replace(" ", "").replace("\n", ""))#[:d.find('\\')])
                    
            elif BLOCK_RULE[file_name] == "URL":
                count = 0
                for d in data:
                    cache_connection.sadd("BLOCK_URL_SET", d.replace(" ", "").replace("\n", ""))

            elif BLOCK_RULE[file_name] == "RE":
                for d in data:
                    cache_connection.sadd("BLOCK_RE_SET", d)

            else:
                for d in data:
                    if len(d) > 4000 or '*' in d:
                        cache_connection.sadd("BLOCK_RE_SET", d[:d.find('\n')])
                    else:
                        cache_connection.sadd("BLOCK_URL_SET", d[:d.find(' ')])
        logger.info("setting blcok set successfully")
        return True
    except Exception as error:
        logger.error(f"""set_block_rule with {error}""")
        return False
    
if __name__ == '__main__':
    set_block_set()
    set_block_rule()

import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.resolve()))
from datetime import datetime, timezone, timedelta
import redis
from data_collection_system import DB_HOST, DB_PORT, DB_DATABASE, CACHE_HOST, CACHE_PORT, CACHE_DATABASE, CACHE_PASSWORD
import pymongo
import random
DIR = f"""{str(pathlib.Path(__file__).parent.resolve())}/file/"""




def get_proxy_ip():
    with open(f"""{DIR}proxy_list.txt""", 'r') as file:
        proxy_ips = file.read().splitlines()
    return random.choice(proxy_ips) 

def get_cache_connection():
    cache_connection = redis.StrictRedis(
        host = CACHE_HOST,
        port = CACHE_PORT,
        db = CACHE_DATABASE,
        password = CACHE_PASSWORD
    )
    return cache_connection

def get_db_connection():
    db_client = pymongo.MongoClient(f"""mongodb://{str(DB_HOST)}:{DB_PORT}/""")
    db = db_client[DB_DATABASE]
    return db

def check_time_format(date_time):
    """
    utility: 檢查時間格式是否符合預設規定
    param  : - date(string): 要檢查的時間
    raise  : - ValueError: 錯誤的時間格式
    """    
    try:
        datetime.strptime(date_time, '%Y/%m/%d %H:%M:%S')
        return True
    except ValueError:
        return False
    
def convert_month(month):
    if month == 'Jan':
        return '01'
    elif month == 'Feb':
        return '02'    
    elif month == 'Mar':
        return '03'  
    elif month == 'Apr':
        return '04'        
    elif month == 'May':
        return '05'        
    elif month == 'Jun':
        return '06'        
    elif month == 'Jul':
        return '07'        
    elif month == 'Aug':
        return '08'        
    elif month == 'Sep':
        return '09'        
    elif month == 'Oct':
        return '10'       
    elif month == 'Nov':
        return '11'     
    else:
        return '12'  
    
def padding(value):
    if len(value) == 1:
        return f"""0{value}"""
    return value

def get_list_from_txt(filename):
    with open(filename, "r") as tf:
        data = tf.read().split('\n')
        return data
    return []

def process_datetime(tmp):
    while '' in tmp:
        del tmp[tmp.index('')]
    date_time = f"""{tmp[4]}/{padding(convert_month(tmp[1]))}/{padding(tmp[2])} {tmp[3]}"""
    return date_time
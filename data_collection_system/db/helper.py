from logging import raiseExceptions
import pymongo
import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.resolve()))
from data_collection_system import DB_HOST, DB_PORT, DB_DATABASE, CACHE_HOST, CACHE_PORT, CACHE_DATABASE, CACHE_PASSWORD

def get_db_connection():
    try:
        db_client = pymongo.MongoClient(f"""mongodb://{str(DB_HOST)}:{DB_PORT}/""")
        db = db_client[DB_DATABASE]
        return db
    except Exception as error:
        raise pymongo.errors.PyMongoError(
            f"Failed to connect to MongoDB with error: "
            f"{error}"
        )

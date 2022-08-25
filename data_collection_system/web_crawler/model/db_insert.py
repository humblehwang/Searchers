from typing import List
from logs import create_logger
from .helper import get_db_connection

logger = create_logger()

def insert_data(data:List[dict], collection_name:str) -> bool:
    """
    Batch insert data to MongoDB

    Args:
        data(List[dict])
        collection_name(str)
    Returns:
        True(bool): Inserting successfully
        False(bool): Failed to insert
    """
    db = get_db_connection()
    collection = db[collection_name]
    try:
        #print(data)
        collection.insert_many(data) 
        #print(collection_name, len(data))
        return True
    except Exception as error:
        logger.error(f"insert_data {collection_name} with {error}")
        return False
from logs import create_logger
from .helper import get_db_connection

logger = create_logger()

def get_latest_url(source: str, board: str) -> str:
    """Get the latest url for target condiction
    
    Args:
        source(str): The data source of article 
        board(str): The board of article
    Returns:
        data[0]['url'](str): A latest url
        empty string: if no data responding to the query
    Raises:
        TypeError: An error caused by wrong type of input params
    """
    try:
        collection = get_db_connection()['article']
        query = {
            "source" : source,
            "board" : board,
        }
        data = list(collection.find(query).sort([("date_time",-1)]).limit(-1))
        if not data:
            return "" 
        return data[0]['url']
    except Exception as error:
        logger.error(
            f"get_latest_url({source}, {board}) with {error}"
        )
        return ""

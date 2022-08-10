"""
utility : 跟Log相關的設定
"""
"""
Add the path of parent of current file into sys.path to let the model, utils and setting modules can be found.
"""
import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.resolve()))
import logging
import datetime
import os
from pytz import timezone, utc

def customTime(*args):
    utc_dt = utc.localize(datetime.datetime.utcnow())
    time_zone = timezone("Asia/Taipei")
    converted = utc_dt.astimezone(time_zone)
    return converted.timetuple()

def create_logger():
    # directory path of log file
    dir_path_log = str(pathlib.Path(__file__).parent.resolve()) + '/file/logging_file/'
    filename_log = str(datetime.datetime.now().strftime("%Y-%m-%d")) + ".log"     
    # if not exist then creat the file
    if not os.path.exists(dir_path_log):
        os.makedirs(dir_path_log)
        
    logging.captureWarnings(True)
    
    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.DEBUG)

    logging.Formatter.converter = customTime

    file_handler = logging.FileHandler(dir_path_log+filename_log, 'a', 'utf-8')
    stream_handler = logging.StreamHandler()

    formatter = logging.Formatter('%(asctime)s - %(lineno)s - %(levelname)s - %(message)s')

    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    """
    logger.info('This is a log info')
    logger.debug('Debugging')
    logger.warning('Warning exists')
    logger.info('Finish')
    """
    return logger

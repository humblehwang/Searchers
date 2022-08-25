from ptt.ptt_url_getter import pttUrlGetter
from ptt.ptt_data_processing import PTTDataProcesser

def ptt_crawler(param:dict) -> None:
    """
    Run PTT crawler by given param

    Args:
        param(dict): A dict of param for PTT crawler
    """
    for carwler in param:
        ptt_url_getter = pttUrlGetter(carwler['is_first'], carwler['board'])
        ptt_data_processer = PTTDataProcesser()
        ptt_url_getter.set_up()
        ptt_data_processer.url_list = ptt_url_getter.url_list
        #print(len(ptt_url_getter.url_list),ptt_url_getter.latest_page_index,ptt_url_getter.latest_url)
        ptt_data_processer.process_articles()

if __name__ == "__main__":
    ptt_param = [
        {"is_first" : False, "board" : "Tech_Job"},
        {"is_first" : False, "board" : "Soft_Job"}
    ]
    ptt_crawler(ptt_param)


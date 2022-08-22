from ptt.ptt_url_getter import pttUrlGetter

if __name__ == "__main__":
    ptt = pttUrlGetter(False, "Tech_Job")
    ptt.latest_url = "https://www.ptt.cc/bbs/Tech_Job/M.1660941577.A.833.html"
    ptt.latest_page_index = ptt.get_latest_page_index()
    print(len(ptt.get_url_list()))
    
    ptt = pttUrlGetter(True, "Tech_Job")
    ptt.latest_url = "https://www.ptt.cc/bbs/Tech_Job/M.1660941577.A.833.html"
    ptt.latest_page_index = 0
    print(len(ptt.get_url_list()))
    
     

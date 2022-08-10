import crawler_ptt_get_article, crawler_ptt_get_url_list

if __name__ == '__main__':
    is_first = False
    target_board = "Tech_Job"
    crawler_ptt_get_url_list.get_url_list(target_board, is_first)
    crawler_ptt_get_article.get_article(target_board)
    
    is_first = False
    target_board = "Soft_Job"
    crawler_ptt_get_url_list.get_url_list(target_board, is_first)
    crawler_ptt_get_article.get_article(target_board)
import crawler_dcard_get_article, crawler_dcard_get_url_list

if __name__ == '__main__':
    is_first = False
    target_board = "tech_job"
    crawler_dcard_get_url_list.get_dcard_url_list(target_board, is_first)
    crawler_dcard_get_article.get_article(target_board)
    

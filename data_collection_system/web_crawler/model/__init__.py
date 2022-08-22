class Article():
    """
    This is an Article class

    Args:
    Attributes:
        _id(str)
        author(str)
        board(str)
        title(str)
        date_time(str)
        source(str)
        num_comment(str)
        url(str)
        article_id(str)
        content(str)
    """

    def __init__(self, params: dict) -> None:
        self._id = ""
        self.author = params['author']
        self.board = params['board']
        self.title = params['title']
        self.date_time = params['date_time']
        self.source = params['source']
        self.num_comment = params['num_comment']
        self.url = params['url']
        self.article_id = params['article_id']
        self.content = params['content']
       
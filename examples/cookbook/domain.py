from gid import Guid


class Article:
    article_id: str
    status: str
    body: str

    def __init__(self, body: str):
        self.article_id = str(Guid())
        self.body = body
        self.status = "unpublished"

    @property
    def ref_id(self):
        return f"article:{self.status}:{self.article_id}"


class ArticleComment:
    article_comment_id: str
    article: Article
    body: str

    def __init__(self, article: Article, body: str):
        self.article_comment_id = str(Guid())
        self.article = article
        self.body = body

from examples.cookbook.application import auth, create_id_generator


class Article:
    article_id: str
    status: str
    body: str

    def __init__(self, body: str):
        self.article_id = get_id("article")
        self.body = body
        self.status = "unpublished"


class ArticleComment:
    article_comment_id: str
    article: Article
    body: str

    def __init__(self, article: Article, body: str):
        self.article_comment_id = get_id("article_comment")
        self.article = article
        self.body = body


get_id = create_id_generator()
article_store = {}


@auth.guard("article:create", "articles:{ article.status }:{ article.article_id }")
def create_article(article: Article) -> Article:
    article_store[article.article_id] = article
    return article


@auth.guard_after("article:read", ref="articles:{ article.status }:{ article.article_id }")
def get_article(article_id: str) -> Article:
    article = article_store[article_id]
    return article


@auth.guard("article:writeComment", ref="articles:{ comment.article.status }:{ comment.article.article_id }")
def create_article_comment(comment: ArticleComment) -> ArticleComment:
    return comment


@auth.guard("article:update", ref="articles:{ article.status }:{ article.article_id }")
def update_article(article: Article, body: str) -> Article:
    article.body = body
    return article


@auth.guard("article:publish")
def publish_article(article: Article) -> Article:
    article.status = "published"
    return article

from dataclasses import dataclass
from application import auth, create_id_generator


@dataclass
class Article:
    article_id: str
    status: str
    body: str


@dataclass
class ArticleComment:
    article_comment_id: str
    article_id: str
    body: str


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


@auth.guard("article:writeComment", ref="articles:{ article.status }:{ article.article_id }")
def create_article_comment(article: Article, comment: str) -> ArticleComment:
    return ArticleComment(get_id(), article.article_id, comment)


@auth.guard("article:update", ref="articles:{ article.status }:{ article.article_id }")
def update_article(article: Article, body: str) -> Article:
    article.body = body
    return article


@auth.guard("article:publish")
def publish_article(article: Article) -> Article:
    article.status = "published"
    return article

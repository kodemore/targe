from examples.cookbook.domain import Article, auth
from targe.errors import AccessDeniedError

actor = auth.authorize("mia_publisher")

article = Article("Lorem Ipsum")
article.status = "published"


@auth.guard(rbac=["writer"])
def create_article(article: Article) -> None:
    ...


try:
    create_article(article)
except AccessDeniedError as e:
    print(f"Access denied: {e}")

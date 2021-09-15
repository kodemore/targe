from targe.errors import AccessDeniedError
from examples.cookbook.domain import auth, Article

actor = auth.authorize("bob_writer")

article = Article("Lorem Ipsum")
article.status = "published"


@auth.guard(rbac=["writer"])
def create_article() -> None:
    ...


try:
    create_article(article)
except AccessDeniedError as e:
    print(e)

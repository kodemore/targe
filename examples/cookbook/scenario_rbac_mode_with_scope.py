from examples.cookbook.domain import Article, auth

actor = auth.authorize("bob_writer")

article = Article("Lorem Ipsum")
article.status = "published"


@auth.guard(scope="article:create", rbac=["writer"])
def create_article(article: Article) -> None:
    ...


create_article(article)

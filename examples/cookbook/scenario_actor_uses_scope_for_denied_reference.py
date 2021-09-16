from examples.cookbook.domain import Article, auth, create_article
from targe.errors import AccessDeniedError

actor = auth.authorize("bob_writer")

article = Article("Lorem Ipsum")
article.status = "published"

try:
    create_article(article)
except AccessDeniedError as e:
    print(e)

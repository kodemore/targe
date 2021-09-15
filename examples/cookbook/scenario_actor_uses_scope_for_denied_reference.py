from targe.errors import AccessDeniedError
from examples.cookbook.domain import auth, create_article, Article

actor = auth.authorize("bob_writer")

article = Article("Lorem Ipsum")
article.status = "published"

try:
    create_article(article)
except AccessDeniedError as e:
    print(e)

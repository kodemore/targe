from toffi.errors import AccessDeniedError
from domain import auth, create_article, Article, get_id

# Tell auth system who is operating at the moment
actor = auth.init("bob_writer")

article = Article(get_id("article"), "published", "Lorem Ipsum")

try:
    new_article = create_article(article)
except AccessDeniedError:
    print("access denied")

from examples.cookbook.domain import auth, create_article, Article

actor = auth.authorize("bob_writer")

article = Article("Lorem Ipsum")

create_article(article)

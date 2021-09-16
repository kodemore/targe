from examples.cookbook.domain import Article, auth, create_article

actor = auth.authorize("bob_writer")

article = Article("Lorem Ipsum")

create_article(article)

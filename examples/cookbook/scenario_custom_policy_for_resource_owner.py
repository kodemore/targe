from examples.cookbook.domain import Article, auth, create_article as base_create_article, update_article
from targe import Policy
from targe.errors import AccessDeniedError


# we need to wrap original create_article function so we can attach
# specific policy for authorised actor once article is being created
@auth.guard("article:create", "articles:{ article.status }:{ article.article_id }")
def create_article(article: Article) -> Article:
    
    # store your article here

    # custom policy for authenticated actor
    auth.actor.policies.append(
        Policy.allow("article:update", f"articles:unpublished:{article.article_id}")
    )
    return article


auth.authorize("bob_writer")
article = Article("Lorem Ipsum")
create_article(article)
article = update_article(article, "Lorem Ipsum Sit")
assert article.body == "Lorem Ipsum Sit"

# now let's authenticate other user with the same roles
auth.authorize("lucas_writer")

try:
    update_article(article, "Lorem Ipsum by Lucas")
except AccessDeniedError as e:
    print(f"Lucas cannot update this article: {e}")

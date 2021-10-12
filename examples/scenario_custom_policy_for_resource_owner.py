from gid import Guid

from targe import Policy, ActorProvider, Actor, Auth
from targe.errors import AccessDeniedError


# This is just an example entity class
class Article:
    article_id: str
    status: str
    body: str

    def __init__(self, body: str):
        self.article_id = str(Guid())
        self.body = body
        self.status = "unpublished"

    @property
    def ref(self):
        return f"{self.status}:{self.article_id}"


# This class will provide an actor to system when Auth.authorize is called
class ProvideBob(ActorProvider):
    def get_actor(self, actor_id: str) -> Actor:
        # we only expect bob in our system
        if actor_id != "bob":
            raise ValueError("Only Bob is allowed.")

        # This is Bob
        bob = Actor("bob")

        # Bob can create articles
        bob.policies.append(Policy.allow("article : create : *"))
        return bob


# Instantiate new auth
auth = Auth(ProvideBob())

# we need to wrap original create_article function so we can attach
# specific policy for authorised actor once article is being created
@auth.guard("article:create")
def create_article(article: Article, actor: Actor) -> Article:
    
    # Perform your logic here

    # custom policy for passed
    actor.policies.append(
        Policy.allow(f"article : update : * : {article.article_id}")
    )
    return article


@auth.guard("article : update : {article.ref}")
def update_article(article: Article) -> Article:
    # Perform your logic here

    return article

# Bob is authorized
bob = auth.authorize("bob")

# Bob creates new article
article = Article("Lorem Ipsum")
create_article(article, bob)

# Bob can update his own articles
article = update_article(article)


# Bob cannot update other articles
try:
    update_article(Article("Other Article"), "Lorem Ipsum by Lucas")
except AccessDeniedError as e:
    print(f"Bob cannot update this article: {e}")

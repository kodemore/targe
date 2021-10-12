from gid import Guid
from targe import Auth, ActorProvider, Actor, Policy


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
    def ref_id(self):
        return f"{self.status}:{self.article_id}"


# This class will provide an actor to system when Auth.authorize is called
class ProvideBob(ActorProvider):
    def get_actor(self, actor_id: str) -> Actor:
        # we only expect bob in our system
        if actor_id != "bob":
            raise ValueError("Only Bob is allowed.")

        # This is Bob
        bob = Actor("bob")
        # Bob has access to article:create scope
        bob.policies.append(Policy.allow("article:create:unpublished"))

        return bob


# Instantiate new auth
auth = Auth(ProvideBob())


# Protect function from unauthorized access
@auth.guard("article:create:{ article.status }")
def create_article(article: Article) -> None:
    # Save your article in database
    # or do other useful things here.
    ...


# Retrieve bob from ActorProvider
auth.authorize("bob")


# This function is called by Bob now
create_article(
    Article("Lorem Ipsum")
)

from examples.cookbook.domain import Article
from targe import Auth, ActorProvider, Actor, Policy


# This class will provide an actor to system when Auth.authorize is called
class ProvideBob(ActorProvider):
    def get_actor(self, actor_id: str) -> Actor:
        # we only expect bob in our system
        if actor_id != "bob":
            raise ValueError("Only Bob is allowed.")

        # This is Bob
        bob = Actor("bob")
        # Bob has access to article:create scope
        bob.policies.append(Policy.allow("article:create"))

        return bob


# Instantiate new auth
auth = Auth(ProvideBob())


# Protect function from unauthorized access
@auth.guard("article:create")
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

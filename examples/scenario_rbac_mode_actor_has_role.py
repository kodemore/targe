from targe import Auth, ActorProvider, Actor, Role


# This class will provide an actor to system when Auth.authorize is called
class ProvideBob(ActorProvider):
    def get_actor(self, actor_id: str) -> Actor:
        # we only expect bob in our system
        if actor_id != "bob":
            raise ValueError("Only Bob is allowed.")

        # This is Bob
        bob = Actor("bob")
        # Bob has editor role
        bob.roles.append(Role("editor"))

        return bob


# Instantiate new auth
auth = Auth(ProvideBob())


# Allow access for users with "editor" role
@auth.guard(roles=["editor"])
def create_article(article) -> None:
    # Perform your logic here.
    ...


# Retrieve bob from ActorProvider
auth.authorize("bob")


# This function is called by Bob now
create_article(
    {"title": "Article Title"}
)

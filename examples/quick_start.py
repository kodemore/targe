from toffi import Auth, AuthStore, Actor, Policy
from toffi.errors import AccessDeniedError


# AuthStore is used by library to retrieve actor
class MyAuthStore(AuthStore):
    def get_actor(self, actor_id: str) -> Actor:
        return Actor(actor_id)


# instantiate auth class
auth = Auth(MyAuthStore())

# initialise auth by passing actor id
auth.init("actor_id")


# `auth.guard` decorator protects function from
# non-authorized access and assigns scope to the function
@auth.guard(scope="protected")
def protect_this() -> None:
    ...  # code that should be protected by auth


try:
    protect_this()
except AccessDeniedError:
    ...  # this will fail as actor has no access to scope `protected`


auth.actor.policies.append(Policy.allow("protected"))  # add `protected` scope to actor policies

protect_this()  # now this works

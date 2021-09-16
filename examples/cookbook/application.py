from typing import Callable

from examples.cookbook import actors
from targe import Actor, ActorProvider, Auth

actor_list = {
    actors.bob.actor_id: actors.bob,
    actors.lucas.actor_id: actors.lucas,
    actors.mia.actor_id: actors.mia,
    actors.john.actor_id: actors.john,
}


# This will provide actor for auth mechanism
class FakePostActorProvider(ActorProvider):
    def get_actor(self, actor_id: str) -> Actor:
        return actor_list[actor_id]


# Create new auth instance
auth = Auth(FakePostActorProvider())


def create_id_generator() -> Callable:
    id_value = 0

    def _get_id(prefix: str = "id") -> str:
        nonlocal id_value
        id_value += 1
        return f"{prefix}_{id_value}"

    return _get_id

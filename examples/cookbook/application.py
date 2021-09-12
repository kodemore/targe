from typing import Callable

import actors
from toffi import Auth, ActorProvider, Actor


actor_list = {
    actors.bob.actor_id: actors.bob,
    actors.lucas.actor_id: actors.lucas,
    actors.mia.actor_id: actors.mia,
    actors.john.actor_id: actors.john,
}


# This will provide actor for auth mechanism
class FakeActorProvider(ActorProvider):
    def get_actor(self, actor_id: str) -> Actor:
        return actor_list[actor_id]


# Initialise auth class
auth = Auth(FakeActorProvider())


def create_id_generator() -> Callable:
    id_value = 0

    def _get_id(prefix: str = "id") -> str:
        nonlocal id_value
        id_value += 1
        return f"{prefix}_{id_value}"

    return _get_id

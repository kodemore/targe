# Toffi
Powerful and flexible policy based authorization library.

## Features
- Customisable and flexible policy system
- Built-in audit log
- Elegant and easy to use
- Non disturbing

## Installation

With pip:
```
pip install toffi
```

or with poetry

```
poetry add toffi
```

## Quick start

```python
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
```

# Usage

## Execution flow
![execution flow](./docs/execution_flow.png)


## Actor

### Persisting actor

## Roles and Policies

### Persisting roles

## Auth

### Guarding function

#### Using scopes

#### Using indexes with resolvers

### Implementing custom behaviour

## Scopes

### Best practices

## Indexes

### Best practices

## Audit log

### Persisting audit log

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
from toffi import Auth, ActorProvider, Actor, Policy
from toffi.errors import AccessDeniedError


# This will provide actor for auth mechanism
class MyActorProvider(ActorProvider):
    def get_actor(self, actor_id: str) -> Actor:
        return Actor(actor_id)


# Initialise auth class
auth = Auth(MyActorProvider())
# Retrieve actor by its id
auth.init("actor_id")


# `auth.guard` decorator assigns auth scope to a function and
# protects it from non-authorized access
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

The following diagram is a high level representation of the execution flow.

![execution flow](./docs/execution_flow.png)

When function gets called, instance of `Auth` class is checking whether `actor` is accessible 
(this should happen when `Auth.init` is called). 
If `actor` is not accessible because `Auth.init` was not called or because `AuthStore.get_user` returned `null` value, 
`UnauthorizedError` exception is raised. 

When `actor` is present, library will try to resolve `index` (index contains a value that is a reference to piece 
of information stored in your application), index resolving will occur if expression passed in `ref` attribute in the `guard` decorator.

Everytime function is being called, library automatically generates audit log, which later on might be used to 
understand how, by who and whether data stored in your system has being changed. 

The last step is execution of guarded function.

## Actor
Actor represents or references to a user in your application. Other important characteristics are:
- an actor aggregates permissions and roles
- an actor encapsulates its state and may act upon its change  
- actor knows whether is can access given scope
- actor's id is referenced in audit log  
- actor can be extended further to encapsulate your application logic 

### Instantiating actor
```python
from toffi import Actor

my_actor = Actor("actor_id")
```

### Assigning policies
```python
from toffi import Actor, Policy

my_actor = Actor("actor_id")

# assign policies 
my_actor.policies.append(Policy.allow("articles:update"))
```

### Assigning roles
```python
from toffi import Actor, Policy, Role

my_actor = Actor("actor_id")

# simple role
user_manager = Role("user_manager")
user_manager.policies.append(Policy.allow("user:*"))

# assign role
my_actor.roles.append(user_manager)
```

### Providing actor to auth system
By default, auth system does not know who is your actor and what it can do. 
To provide information about your actor, you have to implement `toffi.ActorProvider` protocol, 
please consider the following example:

```python
from toffi import ActorProvider, Actor, Auth


class MyActorProvider(ActorProvider):
    def get_actor(self, actor_id: str) -> Actor:
        ... # you can query your database or do other relevant task to factory your instance of `toffi.Actor`
        return Actor(actor_id)

# now we have to just instantiate auth and pass instance of our ActorProvider implementation
auth = Auth(MyActorProvider())

# The following line will cause auth system to use `MyActorProvider.get_actor` method.
auth.init("actor_id")
```

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

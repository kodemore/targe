# Toffi
Powerful and flexible policy based authorization library.

## Features

### Customisable and flexible policy system
Policy system in toffi is not limited to some keywords like `read`, `write`, `create`, etc. 
Instead it uses scopes, which can hold any value that makes sense in your application's domain 
like `eat:salads` adding indexes on the top of that makes it very powerful and flexible system.

### Minimal, close to 0 learning curve
If you already have some experience with other `acl` or `authorization` libraries there is 
almost 0 learning curve. In order to start using this library you will only need 4 methods,
and these are:
- `Auth.guard`
- `Auth.guard_after`
- `Policy.allow`
- `Policy.deny`
- `ActorProvider.get_user`

### Built-in audit log
Everytime guarded function is executed library logs an event, which later on can be persisted
and used to understand who, when, how and what data is being accessed within your application.

### Elegant and easy to use interface
You don't have to write complex `if` statements asserting whether user has given role, policy,
or is authorized. All of it and even more is simply contained for you in one small `@guard`
decorator, which can be attached to any function/method within your codebase and easily moved
away if needed. 


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

When `actor` is present, library will try to resolve `reference` (reference contains a value that points to a piece 
of information stored in your application), reference resolving will occur if expression passed in `ref` attribute 
in the `guard` decorator.

Everytime function is being called, library automatically generates audit log, which later on might be used to 
understand how, by who and whether guarded data in your system has being changed and/or accessed. 

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

## Policies

Policy is an object representing logical rule describing how and what type of information
can be accessed in your application. 
Once policies are created they can ba attached to a role, or a user to ensure fine-grained
access control.

Policies contain `scopes` and `references`. The first ones holds an information how data is 
being accessed within your application (`read`, `write`, `update`, `etc`), 
the latter ones define a rule that might limit accessibility to a single entity 
or entire group of entities. 

The following code snippet shows an example policy that might be used to allow user 
updating articles in specified category `animals`.

```python
from toffi import Policy

policy = Policy.allow(scope="articles:update", ref="articles:animals:*")
```

Having policy above we could also specify an article with an id of `article_id` 
within `animals` category that should not be updated:

```python
from toffi import Policy

policy = Policy.deny("articles:update", "articles:animals:article_id")
```

### Scopes

Scopes can be used to set logical boundaries in your application. These are the boundaries 
in which data is being accessed and/or manipulated. Scope names can contain `:` (namespace separator) 
to improve granularity e.g.: `article:meta:setKeywords`.

Defining policy per scope can be repetitive task, consider the following example:
```python
from toffi import Policy

Policy.allow("article:meta:setKeywords")
Policy.allow("article:meta:setVersion")
Policy.allow("article:meta:setCategory")
Policy.allow("article:meta:getKeywords")
Policy.allow("article:meta:getVersion")
Policy.allow("article:meta:getCategory")
...
```

> Note: if no reference is provided by default everything is accessible within given scope.

In the scenarios like this, `toffi` provides pattern matching mechanism, so the above can be simplified to:

```python
from toffi import Policy

Policy.allow("article:meta:set*")
Policy.allow("article:meta:get*")
```

### References

References can be used to identify and/or logically group your data. References are using similar 
mechanism to scopes, which means in policies definition you can take advantage of `:` (namespace separator)
same way like you do it in the scope definition. 

You can define as many references as needed, as long as they do not collapse, e.g.:
Imagine you have two references expressions, first follows schema `users:{group}:{id}`, 
the other one `users:{group}:{sub-group}:{id}`. 

Let's have a look how pattern matching will work in this scenario:
```
users:{group}:{id}
               +
               |    When matching reference with pattern `users:group:*`, we can match both
               |    all users within all {sub-groups} and all users within a {group},
               |    so having these two references in our application can cause problems.
               +
users:{group}:{sub-group}:{id}
```

Defining additional namespace item can be really helpful in the scenarios like above. 
In order to do that we can follow the corresponding schema:
`{resource_type}:{namespace}:{logical-group-n}:{logical-group-n+1}:{id}`, now let's see this
in action:

```
users:by_group:{group}:{id}
        +
        |   Because we have additonal namespace item which is unique (`by_group` in the first case and `by_subgroup`
        |   in the second case), we can safely use both references together in our application.
        +
users:by_subgroup:{group}:{sub-group}:{id}
```

> Keep in mind you can still give access to all users, simply by using `users:*` pattern. 

## Roles

## Guarding function

### Auth scopes

### Auth references

## Implementing custom behaviour

## Audit log

### Persisting audit log

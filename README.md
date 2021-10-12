# Targe
Powerful and flexible authorization library utilizing policy system that reflects your domain.


## Installation

With pip:
```
pip install targe
```

or with poetry

```
poetry add targe
```

## Quick start

```python
from targe import Auth, ActorProvider, Actor, Policy
from targe.errors import AccessDeniedError


# This will provide actor for auth mechanism
class MyActorProvider(ActorProvider):
    def get_actor(self, actor_id: str) -> Actor:
        return Actor(actor_id)


# Initialise auth class
auth = Auth(MyActorProvider())

# Retrieves and authorizes actor by its id
auth.authorize("actor_id")


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

## Features

### Customisable and flexible policy system
Policy system in **Targe** is not limited to specific keywords like `read`, `write`, `create`, etc. 
Instead it uses scopes, scopes can hold any value that makes sense in your application's domain 
like `salads : eat`. To increase flexibility and control over your domain **Targe** allows for defining dynamic
scopes that can point to specific data in your application.

### Minimal, close to 0 learning curve
If you already have some experience with other `acl` or `authorization` libraries there is 
almost 0 learning curve. In order to start using the library you only need to learn these 5 methods:
- `Auth.guard`
- `Auth.guard_after`
- `Policy.allow`
- `Policy.deny`
- `ActorProvider.get_actor`

### Built-in audit log
Everytime guarded function is executed library creates a log entry. This log entries can be persisted
and used later on to understand who, when, how and what has changed within your application.

### Elegant and easy to use interface
You don't have to write complex `if` statements asserting whether user has given role or policy. 
All of that happens automatically in one small `@guard` decorator, which can be attached to 
any function/method within your codebase and easily removed if needed. 

# Usage

## Execution flow

The following diagram is a high level representation of the execution flow:

![Execution Flow](./docs/targe@2x-2.png)


When protected function gets called, `targe.Auth` class is checking whether `actor` is accessible 
(`targe.Auth.init` is responsible for providing valid instance of `targe.Actor`). 

If for some reason `actor` is not accessible (`Auth.init` was not called or `targe.ActorProvider` has failed) 
`UnauthorizedError` exception is raised. 

When `actor` is present, library will attempt to resolve `scope` and assert whether `actor` has required
policy or access to given scope. Once this is done library will automatically generate an audit log, 
which can be persisted in database for future reference.

Finally, if actor has sufficient rights guarded function is executed, otherwise `targe.AccessDeniedError` is raised.

## Actor
Actor represents authenticated user in your application. Other important characteristics of an actor are:
- an actor aggregates permissions and roles
- an actor encapsulates its state and may act upon its change  
- actor knows whether is can access given scope
- actor's id is referenced in audit log  
- actor can be extended further to encapsulate your application logic 

### Creating new actor

```python
from targe import Actor

my_actor = Actor("actor_id")
```

### Assigning policies

```python
from targe import Actor, Policy

my_actor = Actor("actor_id")

# assign policies 
my_actor.policies.append(Policy.allow("articles : update"))
```

> Note: whitespaces in scope are irrelevant, both `articles:update`, `articles : update`
> are equal from the library points of view.

### Assigning roles

```python
from targe import Actor, Policy, Role

my_actor = Actor("actor_id")

# simple role
user_manager = Role("user_manager")
user_manager.policies.append(Policy.allow("user:*"))

# assign role
my_actor.roles.append(user_manager)
```

### Providing an actor to auth system
By default, auth system does not know who is your actor and what it can do. 

To provide information about your actor, you have to implement `targe.ActorProvider` protocol, 
please consider the following example:

```python
from targe import ActorProvider, Actor, Auth


class MyActorProvider(ActorProvider):
    def get_actor(self, actor_id: str) -> Actor:
        ...  # you can query your database or do other relevant task to factory your instance of `targe.Actor`
        return Actor(actor_id)


# now we have to just instantiate auth and pass instance of our ActorProvider implementation
auth = Auth(MyActorProvider())

# The following line will cause auth system to use `MyActorProvider.get_actor` method.
auth.authorize("actor_id")
```

## Policies

**Policy** is an object representing logical rule that can either allow or deny accessing
certain areas in your application. 
Once policies are created they can ba attached to a role, or a user to ensure fine-grained
access control.

Policies contain `scopes` and `effect`. The first ones holds an information how data is 
being accessed within your application (`read`, `write`, `update`, `etc`), the latter ones 
tell whether scope is accessible or not.

You can define a policy like in the example below:
```python
from targe import Policy

policy = Policy.allow(scope="articles : update")
```

### Scopes

Scope is a string representing a logical boundary within your application in which data is being 
accessed and/or manipulated. This string must follow the pattern [a-zA-Z][a-zA-Z0-9-_]*, whitespaces are ignored.
Characters like: `:`, `,`, `*` are allowed in the scope, but they have specific meaning:

- `:` is used to build namespaced scopes
- `,` is used to match multiple scope sections
- `*` is used for pattern matching expressions

Scopes can be used in policies and in guarded functions. Use scopes in policies to set rules for existing logical 
boundaries in our application. To define those boundaries scopes must be provided in `Auth.guard` decorator, which
decorates given function or method.

The following is a list of valid policy scopes:
```
articles
articles : update
articles : update : article_id
articles : create, upate, delete
articles : *
articles : meta : set-*
articles : meta : *Name
articles : update : * : tags
```

#### Pattern matching

Let's review the following code snippet which defines multiple policies:

```python
from targe import Policy

Policy.allow("article : meta : setKeywords")
Policy.allow("article : meta : setVersion")
Policy.allow("article : meta : setCategory")
Policy.allow("article : meta : getKeywords")
Policy.allow("article : meta : getVersion")
Policy.allow("article : meta : getCategory")
```

It is quite repetitive task which can be simplified by using pattern matching in policy's scopes:

```python
from targe import Policy

Policy.allow("article : meta : set*")
Policy.allow("article : meta : get*")
```

An asterisk at the end of each scope tells **Targe** to use pattern matching mechanism. 
First policy might be interpreted as "match all the scopes which start with `article` namespace followed by `meta` 
namespace followed by namespace that starts with a `set` word". Second one is very similar but last namespace 
has to start with `get` word instead. 

Here are some examples to help you understand how pattern matching works:
```
article : *
```
Match all scopes that start with article namespace.
```
article : * : id
```
Match all scopes that start with an `article`, has `any` namespace after that and ends with a `id`.
```
article : *Name
```
Match all scopes that start with an `article` namespace and are followed by namespace that ends with `Name`

Let's now go back last time to our example that we simplified with pattern matching. This can be simplified 
even further with grouping. Let's consider the following code snippet:

```python
from targe import Policy

Policy.allow("article : meta : set*, get*")
```

Now with the above policy we can match all the scopes that were presented at the beginning of this chapter.

## Roles

Role is a collection of policies with a unique name. Roles can be also 
used to build Role-based access control (RBAC), which is a simplified mechanism
for regulating access to part of your application based on the roles of an individual actor.

The following is an example code, where `user_manager` role is defined:

```python
from targe import Role, Policy

role = Role("user_manager")

# You can also attach policies to a role, but it is not needed in RBAC scenario
role.policies.append(Policy.allow("user : create, update, delete, read"))
```

> Role names must follow [a-z][a-z0-9_-]+ pattern. Role name is also its identifier, 
> thus they should be unique across your application.

## Guarding function

Protecting function from unauthorized access is one of the **Targe**'s main objectives.

We can protect function from unauthorized execution in two styles:
- acl based style
- rbac style

Use rbac style in scenarios where you have to just assert if actor has given role, use acl based style in other cases.
ACL based style is not only giving you more control over your resources but also automatically enables audit log. 

### Guarding function - rbac style example

To protect function from unauthorized execution use `Auth.guard(rbac=[...])` decorator with `rbac` argument. The `rbac`
argument accepts list of strings where each string is a role name that is required in to execute annotated function.

> If more than one role is passed in the `rbac` argument, this means actor has to own all the required roles
> to execute annotated function.

```python
from targe import ActorProvider, Actor, Auth
from targe.errors import AccessDeniedError


class MyActorProvider(ActorProvider):
    def get_actor(self, actor_id: str) -> Actor:
        return Actor(actor_id)


auth = Auth(MyActorProvider())

auth.authorize("actor_id")


@auth.guard(requires=["user_manager"])  # Here we use `Auth.guard` decorator to protect `create_user` function
def create_user() -> None:
    ...


try:
    create_user()
except AccessDeniedError:
    print("`create_user` is protected from unauthorized access.")
```

> Keep in mind you can still take advantage of audit log in rbac mode, 
> the only requirement is to provide `scope` argument in `Auth.guard` decorator.

### Guarding function - acl style example

```python
from targe import ActorProvider, Actor, Auth
from targe.errors import AccessDeniedError

class MyActorProvider(ActorProvider):
    def get_actor(self, actor_id: str) -> Actor:
        return Actor(actor_id)
    
auth = Auth(MyActorProvider())

auth.authorize("actor_id")

@auth.guard(scope="user : create") 
def create_user() -> None:
    ...

try:
    create_user()
except AccessDeniedError:
    print("`create_user` is protected from unauthorized access.") 
```

#### Dynamic scopes

Sometimes you might run in scenarios where you would like to limit access to given entity
or group of entities. In the scenarios like that dynamic scopes might come in handy. 
Dynamic scope contains placeholders for values held by arguments passed to guarded function.
Everytime function is being called placeholders are replaced with corresponding values.

```python
from targe import ActorProvider, Actor, Auth, Policy
from targe.errors import AccessDeniedError

class MyActorProvider(ActorProvider):
    def get_actor(self, actor_id: str) -> Actor:
        # lest initialize actor and allow access to `articles:update:allowed_id` scope.
        actor = Actor(actor_id)
        actor.policies.append(Policy.allow("articles:update:allowed_id"))
        
        return actor
    
auth = Auth(MyActorProvider())

auth.authorize("actor_id")

class Article:
    def __init__(self, article_id: str, body: str):
        self.article_id = article_id
        self.body = body

# Here we define dynamic scope that holds reference to function's parameter `article` 
# and tries to access its property `article_id`
@auth.guard(scope="article : update : { article.article_id }") 
def update_article(article: Article) -> None:
    print("article updated")

# the following attempt will fail as actor has access only to `article:update:allowed_id` scope
try:
    update_article(Article("other_id", "Lorem Ipsum"))
except AccessDeniedError:
    print("`update_article` is protected from unauthorized access.") 

# this line will succeed
update_article(Article("allowed_id", "Lorem Ipsum"))
```

### Overriding function guarding mechanism

You can override default behavior of guard mechanism in scenarios when it denies access to guarded
function. In order to do that pass a callable object to `Auth` initializer, like below:

```python
from targe import ActorProvider, Actor, Auth

class MyActorProvider(ActorProvider):
    def get_actor(self, actor_id: str) -> Actor:
        return Actor(actor_id)
    
def on_guard(actor: Actor, scope: str) -> bool:
    if scope == "user:create":
        return True
    
    return False
    
auth = Auth(MyActorProvider(), on_guard=on_guard)
auth.authorize("actor_id")

@auth.guard(scope="user:create") 
def create_user() -> None:
    ...

create_user()
```

Callable object must return `bool` value (`True` in order to allow access, `False` to deny access) and accept two parameters:
- `actor: targe.Actor` - an actor that is currently authorized in the system
- `scope: str` - scope assigned to guarded function


## Audit log

Audit log might be useful if you need to track actor's activities in your application.
By default, all actor's actions against guarded functions are automatically recorded and stored
in memory as long as `scope` attribute is provided in the `Auth.guard` decorator. 

> `InMemoryAuditStore` class is a default in-memory implementation of `AuditStore` protocol, which
> is instantiated by `Auth` class if no other implementation is provided.


### AuditEntry structure

`targe.AuditEntry` is a representation of a single actor's action against guarded function in your application.

Each audit entry contains the following information:
- **`entry_id`**: `str` - unique identifier 16 characters long
- **`actor_id`**: `str` - id of authenticated actor may reference to a user in your application
- **`scope`**: `str` - scope in which function was executed, defined in guard decorator
- **`status`**: `targe.AuditStatus` - tells whether execution of a guarded function was successful or not
- **`created_on`**: `datetime.datetime` - the time when action was initialized

### Persisting audit log

As we already discussed by default audit log is stored only in the memory, this behaviour 
can be simply amended by implementing `targe.AuditStore` protocol and passing instance
of new implementation into `targe.Auth`'s initializer:

```python
from targe import AuditStore, AuditEntry, Auth, ActorProvider, Actor
import sqlite3


class MyActorProvider(ActorProvider):
    def get_actor(self, actor_id: str) -> Actor:
        return Actor(actor_id)

    
class MyAuditStore(AuditStore):
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        
    def append(self, log: AuditEntry) -> None:
        query = self.connection.cursor()
        query.execute(
            "INSERT INTO audit_log VALUES(?, ?, ?, ?, ?)",
            (
                log.entry_id,
                log.actor_id,
                log.scope,
                log.status,
                log.created_on
             )
        )
        
db_connection = sqlite3.connect("audit_log.db")
auth = Auth(actor_provider=MyActorProvider(), audit_store=MyAuditStore(db_connection))
auth.authorize("actor_id")
...
```

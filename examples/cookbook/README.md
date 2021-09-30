# FakePost Cookbook

## What is it?
This directory is a showcase project. It will help you to understand how to define roles, permissions, actors
and how to use all of it in production application on different scenarios.

## The story
Imagine you have to write an application to help new company **FakePost** bring their newspaper to
digital world. 

You call them to gather business requirements. It goes well, the complete feature list is as follows:
- manage `articles`
- serve `articles` to **FakePost**'s `subscribers` 
- allow `subscribers` to leave `comment` under `published articles`

Does not sound too complex, but you learn the company has a certain structure, that you have to include in your design. 
The structure within company involves 3 different roles:
- `owner`
- `writer`
- `publisher`

Each of the role have different responsibilities:

- **owner** has access to `everything`
- **writer** can `create` new un-published articles, `read` all articles in the system and `update` their own articles
- **publisher** can `read` all articles and `publish` them for `subscribers`

## How this cookbook is organised

- [`policies.py`](policies.py) - contains various policies used by `roles.py`
- [`roles.py`](roles.py) - contains role definitions (owner, publisher, writer, subscriber)
- [`actors.py`](actors.py) - defines few example users with different roles
- [`domain.py`](domain.py) - application's domain code with example functions guarded by the library
- `scenario_*.py` - example use case scenarios

### Scenarios

To run scenarios simply run any file which name starts with `scenario_` suffix.
Before running scenarios it is recommended to get familiar with code in the
non-scenario files located in the same directory.

#### Actor uses scope for allowed reference

This is an example successful scenario, where user with `writer` role is allowed 
to perform `article:create` action on article referenced by `article:unpublished:*`.

[Click here to see the code](scenario_actor_uses_allowed_static_scope.py)

#### Actor uses scope for denied reference

This scenario results in `toffi.errors.AccessDeniedError`, as user with `writer` role
is not allowed to perform `article:create` action on articles in published state.

The exception is caught in try/except clause, and error is printed out.

[Click here to see the code](scenario_actor_uses_scope_for_denied_reference.py)

#### Actor has unique policy for specific resource

This scenario shows how to attach specific policy for a given actor,
so it gains more access over given resource compared to other actors 
who can share the same roles.

[Click here to see the code](./scenario_custom_policy_for_resource_owner.py)

#### Rbac mode, actor has required role

This scenario shows how to use targe in rbac mode, where actor is only
required to has given role.

[Click here to see the code](./scenario_custom_policy_for_resource_owner.py)

# FakePost Cookbook

## What it is
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

- [`policies.py`](./policies.py) - contains various policies used by `roles.py`
- [`roles.py`](./roles.py) - contains role definitions (owner, publisher, writer, subscriber)
- [`actors.py`](./actors.py) - defines few example users with different roles
- [`domain.py`](./domain.py) - application's domain code with example functions guarded by the library
- `scenario_*.py` - example use case scenarios

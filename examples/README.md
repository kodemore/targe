# Examples

## What is it?
This directory contains example scenarios. It will help you to understand how to define roles, permissions, actors
and how to use all of it in production application on different scenarios.

## Scenarios

### Quick start

The fastest way to get started with `Targe`.

[Click here to see the code](quick_start.py)

### Actor uses allowed static scope 

This is an example scenario, where user is assigned a `policy` which allow
accessing `article:create` scope.

[Click here to see the code](scenario_static_scope_example.py)

### Actor uses allowed dynamic scope

This is an example scenario, where user is assigned a `policy` which allow
accessing `article:create:unpublished` scope. The scope is calculated dynamically
just before the execution (line 40)

[Click here to see the code](scenario_dynamic_scope_example.py)


### Actor uses denied scope

This scenario results in `toffi.errors.AccessDeniedError`, as user is not allowed 
to access `article:create` scope.

The exception is caught in try/except clause, and error is printed out.

[Click here to see the code](scenario_denied_scope_example.py)

### Actor has unique policy for specific scope

This scenario shows how to attach specific policy for a given actor,
so it gains access to specific scope.

[Click here to see the code](scenario_custom_policy_for_resource_owner.py)

### Rbac mode

This scenario shows how to use targe in rbac mode. The example covers a scenario where actor
has a required role.

[Click here to see the code](scenario_rbac_mode_actor_has_role.py)

The following scenario shows what happens when actor does not have specified role.

[Click here to see the code](scenario_rbac_mode_actor_is_missing_role.py)

### Persisting audit log

In this scenario we will look how we can store automatically generated audit log in
a file.

[Click here to see the code](persisting_audit_log.py)

[Click here to see example log file](log.txt)

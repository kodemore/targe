from targe import Actor, ActorProvider, Auth, Policy, AuditStore, AuditEntry
from targe.errors import AccessDeniedError


# This class will handle persisting log to a file
class MyAuditStore(AuditStore):
    def __init__(self, file_path: str):
        self.audit = []
        self.file_path = file_path

    def append(self, log: AuditEntry) -> None:
        self.audit.append(log)

    def flush(self) -> None:
        with open(self.file_path, "a") as file:
            file.writelines([str(entry) + "\n" for entry in self.audit])


class MyActorProvider(ActorProvider):
    def get_actor(self, actor_id: str) -> Actor:
        return Actor(actor_id)


# Initialise audit log
audit_log = MyAuditStore("./log.txt")

auth = Auth(MyActorProvider(), audit_log)
auth.authorize("actor_id")


@auth.guard(scope="protected")
def protect_this() -> None:
    ...  # code that should be protected by auth


try:
    protect_this()
except AccessDeniedError:
    ...  # failures are stored in audit

auth.actor.policies.append(
    Policy.allow("protected")
)

protect_this()  # successes are stored in audit as well


# Flush audit
audit_log.flush()

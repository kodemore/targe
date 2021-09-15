from targe import Actor
from examples.cookbook import roles

bob = Actor("bob_writer")
bob.roles.append(roles.writer)

lucas = Actor("lucas_writer")
lucas.roles.append(roles.writer)

mia = Actor("mia_publisher")
mia.roles.append(roles.publisher)

john = Actor("john_subscriber")
john.roles.append(roles.subscriber)

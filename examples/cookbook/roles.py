import policies
from toffi import Role

owner = Role("owner")
owner.policies.append(policies.allow_everything_on_article)

writer = Role("writer")
writer.policies.append(policies.allow_create_on_articles)
writer.policies.append(policies.allow_read_on_articles)

publisher = Role("publisher")
publisher.policies.append(policies.allow_read_on_articles)
publisher.policies.append(policies.allow_publish_on_articles)
publisher.policies.append(policies.allow_un_publish_on_articles)


subscriber = Role("subscriber")
subscriber.policies.append(policies.allow_read_on_published_articles)
subscriber.policies.append(policies.allow_create_comment_on_published_article)

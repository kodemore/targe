from targe import Policy

# System policies
allow_everything_on_article = Policy.allow("article:*")

allow_read_on_published_articles = Policy.allow("article:read", "articles:published:*")
allow_read_on_articles = Policy.allow("article:read", "articles:*")
allow_create_on_articles = Policy.allow("article:create", "articles:unpublished:*")
allow_publish_on_articles = Policy.allow("article:publish", "articles:*")
allow_un_publish_on_articles = Policy.allow("article:un-publish", "articles:*")
allow_create_comment_on_published_article = Policy("article:createComment", "articles:published:*")

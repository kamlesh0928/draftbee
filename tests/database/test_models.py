from sqlalchemy.orm import configure_mappers
from app.database.models import Topic, Post, Source


def test_mappers_configure_without_error():
    configure_mappers()


def test_post_belongs_to_topic(db_session):
    topic = Topic(name="System Design")
    post = Post(title="Load Balancers 101", content="...", topic=topic)
    db_session.add(post)
    db_session.commit()

    assert post.topic.name == "System Design"
    assert topic.posts == [post]


def test_source_links_back_to_post(db_session):
    topic = Topic(name="AI/ML")
    post = Post(title="Caching Strategies", content="...", topic=topic)
    source = Source(name="HN", url="https://news.ycombinator.com/x", post=post)
    db_session.add(source)
    db_session.commit()

    assert source.post.title == "Caching Strategies"
    assert post.sources == [source]

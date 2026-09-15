from app.database.models.topic import (
    STATUS_PENDING,
    STATUS_REJECTED,
    STATUS_USED,
    Topic,
)
from app.discovery import repository


def test_save_topics_persists_all_ideas_as_pending(mocker, session_factory):
    mocker.patch("app.discovery.repository.SessionLocal", session_factory)

    ideas = [
        {"title": f"Idea {i}", "description": f"Desc {i}", "rank": i, "explanation": f"Why {i}"}
        for i in range(1, 4)
    ]

    saved = repository.save_topics(ideas)

    assert len(saved) == 3
    assert all(topic.status == STATUS_PENDING for topic in saved)
    assert all(topic.id is not None for topic in saved)


def test_get_pending_topics_returns_only_pending_ordered_by_rank(mocker, session_factory):
    mocker.patch("app.discovery.repository.SessionLocal", session_factory)

    with session_factory() as session:
        session.add_all(
            [
                Topic(title="Used", rank=1, status=STATUS_USED),
                Topic(title="Second", rank=2, status=STATUS_PENDING),
                Topic(title="First", rank=1, status=STATUS_PENDING),
            ]
        )
        session.commit()

    pending = repository.get_pending_topics()

    assert [t.title for t in pending] == ["First", "Second"]


def test_mark_topic_status_updates_existing_topic(mocker, session_factory):
    mocker.patch("app.discovery.repository.SessionLocal", session_factory)

    with session_factory() as session:
        topic = Topic(title="Some idea", rank=1, status=STATUS_PENDING)
        session.add(topic)
        session.commit()
        topic_id = topic.id

    repository.mark_topic_status(topic_id, STATUS_REJECTED)

    with session_factory() as session:
        refreshed = session.get(Topic, topic_id)
        assert refreshed.status == STATUS_REJECTED


def test_mark_topic_status_silently_ignores_missing_topic(mocker, session_factory):
    mocker.patch("app.discovery.repository.SessionLocal", session_factory)

    repository.mark_topic_status(999999, STATUS_REJECTED)

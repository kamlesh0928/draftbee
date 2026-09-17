from app.discord.embeds import build_post_preview_embed


def test_build_post_preview_embed_contains_platform_content():
    embed = build_post_preview_embed("Caching 101", "LinkedIn body", "X body")

    assert embed.title == "New post idea: Caching 101"
    assert embed.fields[0].name == "LinkedIn"
    assert embed.fields[0].value == "LinkedIn body"
    assert embed.fields[1].name == "X"
    assert embed.fields[1].value == "X body"


def test_build_post_preview_embed_truncates_long_content():
    long_text = "a" * 2000

    embed = build_post_preview_embed("Topic", long_text, long_text)

    assert len(embed.fields[0].value) == 1024
    assert len(embed.fields[1].value) == 1024

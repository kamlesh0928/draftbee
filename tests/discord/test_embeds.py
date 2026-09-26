from app.discord.embeds import build_post_preview_embed


def test_build_post_preview_embed_contains_platform_content():
    embed = build_post_preview_embed("Caching 101", "LinkedIn body with #hashtags")  # Add `X body` this in the parameter when posting on X as well.

    assert embed.title == "New post idea: Caching 101"
    assert embed.description == "LinkedIn body with #hashtags"

    # Uncomment - If added credits on X platform.
    # assert embed.fields[1].name == "X"
    # assert embed.fields[1].value == "X body"


def test_build_post_preview_embed_truncates_long_content():
    long_text = "a" * 5000

    embed = build_post_preview_embed("Topic", long_text) # Add `long_text` this in the parameter when posting on X as well.

    assert len(embed.description) == 4096
    # assert len(embed.fields[1].value) == 4096     # Uncomment - If added credits on X platform.

import discord


def build_post_preview_embed(topic_title: str, linkedin_content: str, x_content: str) -> discord.Embed:
    embed = discord.Embed(
        title=f"New post idea: {topic_title}",
        color=discord.Color.blurple(),
    )

    embed.add_field(name="LinkedIn", value=linkedin_content[:1024], inline=False)
    embed.add_field(name="X", value=x_content[:1024], inline=False)
    return embed

import discord
from discord import Webhook, AsyncWebhookAdapter
import aiohttp
import asyncio
import os
from datetime import datetime

TOKEN = os.environ.get("DISCORD_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

if not TOKEN or not WEBHOOK_URL:
    print("DISCORD_TOKEN veya WEBHOOK_URL environment variable eksik!")
    exit(1)

intents = discord.Intents.default()
intents.messages = True
intents.dm_messages = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"{client.user} giriş yaptı → DM'leri dinliyorum...")

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    if not isinstance(message.channel, discord.DMChannel):
        return

    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(WEBHOOK_URL, adapter=AsyncWebhookAdapter(session))

        embed = discord.Embed(
            description=message.content or "*Mesaj içeriği yok (embed/sticker olabilir)*",
            color=0x5865F2,
            timestamp=message.created_at
        )

        embed.set_author(
            name=str(message.author),
            icon_url=message.author.display_avatar.url if message.author.display_avatar else None
        )

        embed.set_footer(text=f"User ID: {message.author.id} • Mesaj ID: {message.id}")

        if message.attachments:
            embed.add_field(
                name="Ek Dosya(lar)",
                value="\n".join([att.filename for att in message.attachments]),
                inline=False
            )

        await webhook.send(
            content="**Yeni DM geldi!**",
            embed=embed,
            username="DM Bildirim Botu",
            # avatar_url="https://i.imgur.com/istediğin_resim.png"  # opsiyonel
        )

        print(f"Yönlendirildi → {message.author}: {message.content[:60]}...")

async def main():
    async with client:
        await client.start(TOKEN, reconnect=True)

if __name__ == "__main__":
    asyncio.run(main())
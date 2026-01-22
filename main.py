import discord
from discord import Webhook, AsyncWebhookAdapter
import aiohttp
import asyncio
import os
from datetime import datetime

TOKEN = os.environ.get("DISCORD_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

if not TOKEN or not WEBHOOK_URL:
    print("DISCORD_TOKEN veya WEBHOOK_URL eksik!")
    exit(1)

intents = discord.Intents.default()
intents.messages = True
intents.dm_messages = True

client = discord.Client(intents=intents)

HEARTBEAT_INTERVAL = 600  # saniye cinsinden → 10 dakika
last_message_time = datetime.utcnow()  # başlangıç zamanı

async def send_heartbeat():
    global last_message_time
    while True:
        await asyncio.sleep(HEARTBEAT_INTERVAL)
        now = datetime.utcnow()
        if (now - last_message_time).total_seconds() >= HEARTBEAT_INTERVAL:
            # Son HEARTBEAT_INTERVAL kadar sürede DM gelmedi → heartbeat at
            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(WEBHOOK_URL, adapter=AsyncWebhookAdapter(session))
                embed = discord.Embed(
                    title="Bot Aktif",
                    description="Son 10 dakikada yeni DM gelmedi.",
                    color=0x00FF00,  # Yeşil
                    timestamp=now
                )
                embed.set_footer(text="Heartbeat - Selfbot çalışıyor")
                await webhook.send(
                    content="**Heartbeat**",
                    embed=embed,
                    username="DM Bildirim Botu",
                )
            print("Heartbeat gönderildi: Yeni DM yok")

@client.event
async def on_ready():
    print(f"{client.user} giriş yaptı → DM dinleniyor...")
    client.loop.create_task(send_heartbeat())  # heartbeat'i arka planda başlat

@client.event
async def on_message(message: discord.Message):
    global last_message_time
    if message.author == client.user:
        return

    if not isinstance(message.channel, discord.DMChannel):
        return

    # Zamanı güncelle (yeni mesaj geldi)
    last_message_time = datetime.utcnow()

    # Mevcut mesaj gönderme kodun buraya devam eder...
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(WEBHOOK_URL, adapter=AsyncWebhookAdapter(session))

        embed = discord.Embed(
            description=message.content or "*İçerik yok*",
            color=0x5865F2,
            timestamp=message.created_at
        )
        embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url if message.author.display_avatar else None)
        embed.set_footer(text=f"ID: {message.author.id}")

        if message.attachments:
            embed.add_field(name="Dosya", value="\n".join(a.filename for a in message.attachments), inline=False)

        await webhook.send(content="**Yeni DM!**", embed=embed, username="DM Bildirim")

        print(f"DM yönlendirildi → {message.author}")

async def main():
    async with client:
        await client.start(TOKEN, reconnect=True)

if __name__ == "__main__":
    asyncio.run(main())
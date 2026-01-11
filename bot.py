import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import hmac
import hashlib
import time

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
SECRET_KEY = os.getenv("SIGNING_SECRET", "default_secret_key_change_me")
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

class LinkBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}")

bot = LinkBot()

def generate_signature(user_id):
    """
    ユーザーIDとタイムスタンプを署名して、改ざんを防ぐ。
    """
    timestamp = str(int(time.time()))
    message = f"{user_id}:{timestamp}".encode()
    sig = hmac.new(SECRET_KEY.encode(), message, hashlib.sha256).hexdigest()
    return f"{timestamp}.{sig}"

@bot.tree.command(name="link", description="X (Twitter) アカウントを連携します")
async def link(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    sig = generate_signature(user_id)
    
    # 署名付き URL を生成
    link_url = f"{BASE_URL}/start?user_id={user_id}&sig={sig}"
    
    embed = discord.Embed(
        title="X アカウント連携",
        description="以下ボタンをクリックして X (Twitter) との連携を開始してください。マッピングの安全性を確保するため、このリンクは24時間有効です。",
        color=0x1DA1F2 # X Blue
    )
    
    view = discord.ui.View()
    button = discord.ui.Button(label="Xでログイン", url=link_url)
    view.add_item(button)
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

if __name__ == "__main__":
    if not TOKEN:
        print("Error: DISCORD_BOT_TOKEN is not set in .env file.")
    else:
        bot.run(TOKEN)

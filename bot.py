import os
import discord
import requests
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
ALLOWED_ROLE_ID = int(os.getenv("ALLOWED_ROLE_ID"))
API_URL = os.getenv("API_URL", "http://localhost:5000")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree


def is_authorized(interaction: discord.Interaction) -> bool:
    return any(role.id == ALLOWED_ROLE_ID for role in interaction.user.roles)


@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Logged in as {bot.user} (slash commands synced)")


@tree.command(name="ban", description="Ban a player by UserId")
@app_commands.describe(userid="Roblox UserId",
                       reason="Reason for ban",
                       day="Number of days (e.g., 7)")
async def ban(interaction: discord.Interaction, userid: str, reason: str,
              day: int):
    if not is_authorized(interaction):
        await interaction.response.send_message(
            "❌ You don't have permission to use this command.", ephemeral=True)
        return

    data = {"command": "ban", "userid": userid, "reason": reason, "day": day}
    requests.post(f"{API_URL}/send_command", json=data)
    await interaction.response.send_message(
        f"✅ Ban `{userid}` for `{day}` day(s). 📌 Reason: {reason}")


@tree.command(name="kick", description="Kick a player by UserId")
@app_commands.describe(userid="Roblox UserId", reason="Reason for kick")
async def kick(interaction: discord.Interaction, userid: str, reason: str):
    if not is_authorized(interaction):
        await interaction.response.send_message(
            "❌ You don't have permission to use this command.", ephemeral=True)
        return

    data = {"command": "kick", "userid": userid, "reason": reason}
    requests.post(f"{API_URL}/send_command", json=data)
    await interaction.response.send_message(
        f"✅ Kick `{userid}`. 📌 Reason: {reason}")


@tree.command(name="unban", description="Unban a player by UserId")
@app_commands.describe(userid="Roblox UserId", reason="Reason for unban")
async def unban(interaction: discord.Interaction, userid: str, reason: str):
    if not is_authorized(interaction):
        await interaction.response.send_message(
            "❌ You don't have permission to use this command.", ephemeral=True)
        return

    data = {"command": "unban", "userid": userid, "reason": reason}
    requests.post(f"{API_URL}/send_command", json=data)
    await interaction.response.send_message(
        f"✅ Unban `{userid}`. 📌 Reason: {reason}")


@tree.command(
    name="check",
    description="Check how many players are currently online in the game")
async def check(interaction: discord.Interaction):
    if not is_authorized(interaction):
        await interaction.response.send_message(
            "❌ You don't have permission to use this command.", ephemeral=True)
        return

    try:
        res = requests.get(f"{API_URL}/get_players")
        data = res.json()
        await interaction.response.send_message(
            f"👥 There are currently `{data['count']}` players in the game.")
    except Exception as e:
        await interaction.response.send_message(
            f"⚠️ Error fetching data from the server: {e}", ephemeral=True)


# Allow running standalone or being imported
if __name__ == "__main__":
    bot.run(TOKEN)

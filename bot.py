import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# Charger le fichier .env dans le même dossier que ce script
load_dotenv(".env")
TOKEN = os.getenv("DISCORD_TOKEN")

if TOKEN is None:
    raise ValueError("Le token Discord n'a pas été trouvé. Vérifie ton fichier .env !")

# Création du bot
intents = discord.Intents.default()
intents.message_content = True  # nécessaire pour lire le contenu des messages
bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionnaire pour stocker les résidences
residences = {}

@bot.event
async def on_ready():
    print(f"{bot.user} est connecté et prêt !")

# Commande pour créer une résidence
@bot.command()
async def creer_residence(ctx):
    member = ctx.author
    if member.id in residences:
        await ctx.send(f"{member.mention}, tu as déjà une résidence.")
        return

    category = ctx.channel.category
    if category is None:
        await ctx.send("Cette commande doit être utilisée dans un salon appartenant à une catégorie.")
        return

    # Création du salon
    guild = ctx.guild
    salon = await guild.create_text_channel(f"{member.name}-residence", category=category)
    residences[member.id] = salon.id

    await salon.send(f"Bienvenue dans ta nouvelle résidence {member.mention} !")
    await ctx.send(f"Résidence créée : {salon.mention}")

# Commande pour renommer sa résidence
@bot.command()
async def renommer_residence(ctx, *, nouveau_nom):
    member = ctx.author
    if member.id not in residences:
        await ctx.send(f"{member.mention}, tu n'as pas encore de résidence.")
        return

    salon_id = residences[member.id]
    salon = ctx.guild.get_channel(salon_id)
    if salon is None:
        await ctx.send("Impossible de trouver ta résidence.")
        return

    await salon.edit(name=nouveau_nom)
    await ctx.send(f"Résidence renommée en {nouveau_nom} !")

# Commande pour inviter plusieurs membres
@bot.command()
async def inviter(ctx, *membres: discord.Member):
    member = ctx.author
    if member.id not in residences:
        await ctx.send(f"{member.mention}, tu n'as pas encore de résidence.")
        return

    salon_id = residences[member.id]
    salon = ctx.guild.get_channel(salon_id)
    if salon is None:
        await ctx.send("Impossible de trouver ta résidence.")
        return

    for m in membres:
        await salon.set_permissions(m, read_messages=True, send_messages=True)

    mentions = ", ".join(m.mention for m in membres)
    await salon.send(f"{mentions} ont été invités dans la résidence de {member.mention} !")
    await ctx.send(f"{mentions} ont été invités dans ta résidence.")

# Commande pour expulser un membre
@bot.command()
async def expulser(ctx, member: discord.Member):
    if ctx.author.id not in residences:
        await ctx.send("Tu n'as pas de résidence !")
        return

    channel = residences[ctx.author.id]["channel"]
    await channel.set_permissions(member, overwrite=None)
    if member.id in residences[ctx.author.id]["invites"]:
        residences[ctx.author.id]["invites"].remove(member.id)

    await channel.send(f"{member.mention} a été expulsé de la résidence.")
    await ctx.send(f"{member.mention} n'a plus accès à ta résidence.")

# Commande pour supprimer sa résidence
@bot.command()
async def supprimer_residence(ctx):
    if ctx.author.id not in residences:
        await ctx.send("Tu n'as pas de résidence !")
        return

    channel = bot.get_channel(residences[ctx.author.id]["channel_id"])
    await channel.delete()
    del residences[ctx.author.id]
    save_residences()
    await ctx.send("Ta résidence a été supprimée.")

bot.run(TOKEN)

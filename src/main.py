import discord
from discord import app_commands
import json
import yfinance as yf


f = open("src/config.json", "r")
token = json.loads(f.read())


MY_GUILD = discord.Object(id=1086131548585201725)


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
client = MyClient(intents=intents)


@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print("------")


@client.tree.command()
async def summary(interaction: discord.Interaction, ticker: str):
    try:
        info = yf.Ticker(ticker).info
        at_close = info["currentPrice"]
        at_prev_close = info["regularMarketPreviousClose"]
        currency = info["currency"]
        industry = info["industry"]
        country = info["country"]
        exchange = info["exchange"]

        change = round(at_close - at_prev_close, 2)
        percent_change = round(((at_close - at_prev_close) / at_prev_close) * 100, 2)

        if at_close >= at_prev_close:
            color = discord.Color.green()
            signed_change = "+"
        else:
            color = discord.Color.red()
            signed_change = ""

        if info["country"] == "United States":
            location = f'{info["city"]}, {info["state"]}'
        else:
            location = f'{info["city"]}, {info["country"]}'

        embed = discord.Embed(
            title=f"({info['symbol']}) {info['longName']}: {at_close}",
            description=(
                f"{exchange} · {currency} \n"
                f"Industry: {industry} \n"
                f"Location: {location} \n\n"
                f"Previous close: {at_prev_close} \n"
                f"Change: {signed_change}{change} ({signed_change}{percent_change}%) \n"
            ),
            color=color,
        )
        # print(info)
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("Ticker not found")


client.run(token)

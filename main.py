import json
import os, sys

#0. Import the latest discordpy (Not the stable, it is the version 2.0x)
directory = os.getcwd()
sys.path.insert(0, directory+"\lib")
import discord
from discord import app_commands

#0.5 Import all submodules
from lib import data
from lib import vc_dynamic
from lib import vc_moderation
from lib import chatbot
from lib import s_command
import asyncio

#1. Read and Load Configs.
with open("data/config.json", encoding="utf-8") as configFile:
    config = json.load(configFile)
bot_token = config["token"]
bot_invite = config["invite"]


#2. Initialize Client Object (Note: To implement slash command, we must use CommandTree.
class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
    async def setup_hook(self):
        for connected_guild in client.guilds:
            #print(connected_guild.id)
            MY_GUILD = discord.Object(id=connected_guild.id)
            self.tree.copy_global_to(guild=MY_GUILD)
            await self.tree.sync(guild=MY_GUILD)
intents = discord.Intents.all()
client = MyClient(intents=intents)


#3. All kind of events and commands.
@client.event
async def on_ready():
    await client.setup_hook()
    print('龙x蓝准备就绪!')
    
@client.event
async def on_message(message):
    if data.is_monitor_chat_channel(message.channel.id):
        async with ctx.typing():
            await asyncio.sleep(2)
        await chatbot.input_chat(message,client)                 #3.1 Chatbot.
    
@client.event
async def on_voice_state_update(member, before, after):
    if after.channel is not None:                    
        if data.is_monitor_channel(after.channel.id):
            await vc_dynamic.process_changes(member, after)      #3.2 Dynamic Voice Channels - Join VC.
    else:
        if data.is_monitor_subchannel(before.channel.id): 
            if len(before.channel.voice_states.keys()) == 0:
                await vc_dynamic.close_subchannel(before)         #3.2 Dynamic Voice Channels - Leave VC.

    await vc_moderation.process_vc_action(member, before,        #3.3 Mute, Deafen, Stream - Action Moderation.
                                        after, client)
@client.tree.command()
async def setup(interaction: discord.Interaction):
    reply = await s_command.setup(interaction.guild,client)      #3.4 Slash Command - Setup.
    await interaction.response.send_message(f'{reply}')


#4. Run the bot.
client.run(bot_token)

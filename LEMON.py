"""
This is the pilot script for the Discord bot created by students of Texas Tech University's
Tech Robotics Association to aid with the growth of the Texas Robotics scenes
"""

import discord #API module
import os      #Machine hosting LEMON
from dotenv import load_dotenv  #imports secrets from the enviornment
from time import sleep

import message_handling as msg_handle

load_dotenv()

#init some variables for L.E.M.O.N
client = discord.Client() #send request to Discord API
token = os.getenv('TOKEN')  #get and init the token
#specify intents
discord.Intents.all()

#initalize L.E.M.O.N
@client.event
async def on_ready():
    #notify clean login
    print(f"{client.user} successfully logged in.")

#Runtime of bot:
client.run(token)

#Subject to change:
#Logistics
#Experiment
#Made with
#Organized and
#Nifty code

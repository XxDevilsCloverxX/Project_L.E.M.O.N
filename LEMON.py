"""
This is a discord bot created by students of Texas Tech University's
Tech Robotics Association to aid with the growth of the Texas Robotics scenes
"""
import discord  #bot commands and API
import os   #for the machine hosting LEMON
from dotenv import load_dotenv  #importing .env from host machine
import requests #reaching webpages to scrape data related to lookup
from bs4 import BeautifulSoup

#import .env secrets
load_dotenv()

#init some variables for L.E.M.O.N
client = discord.Client() #send request to Discord API
token = os.getenv('TOKEN')  #get and init the token

#initalize L.E.M.O.N
@client.event
async def on_ready():
    print(f"{client.user} successfully logged in.")

"""
This is a global declaration block of variables that can be used
during LEMON's runtime...must be updated manually as games are released
"""
command_names = ("/lemonhelp","/purge","/play <url>") #tuple of command names LEMON users can access, function names are unique
manuals = {
"FTC": tuple(["https://www.firstinspires.org/sites/default/files/uploads/resource_library/ftc/game-manual-part-1-traditional-events.pdf", "https://www.firstinspires.org/sites/default/files/uploads/resource_library/ftc/game-manual-part-2-traditional.pdf"]),
"GEAR": tuple(["https://www.youtube.com/watch?v=tXWykG-8_Mw&list=PLJR32U_dICxeLXuzJeBRt3xAuo1TEZHdZ"]),
"VOLUNTEER": tuple(["https://www.firstinspires.org/resource-library/ftc/volunteer-resources"]),
"PROGRAMMING": tuple(["https://www.firstinspires.org/resource-library/ftc/technology-information-and-resources"]),
"FLL":tuple(["https://www.youtube.com/watch?v=tXWykG-8_Mw&list=PLJR32U_dICxeLXuzJeBRt3xAuo1TEZHdZ"]),
"MENTORSHIP": tuple(["https://www.techroboticsassociation.org/", "https://info.firstinspires.org/mentor-network"])
}   #dictionary containing online resource urls for the games, possibly .txts in the future

#greet a new memeber
@client.event
async def on_member_join(member):
    if member.dm_channel == None:
        await id = member.create_dm()   #create a new dm channel
    direct_channel = member.dm_channel
    await direct_channel.send(f"Salutations {member.name}! I am L.E.M.O.N, responsible for aiding everyone in the guild. Enjoy your stay! And feel free to check my open-source repo at: {None}")
    return None

#ping a departing member in private that we appreciate their time here
@client.event
async def on_member_remove(member):
    if member.dm_channel == None:
        await id = member.create_dm()   #create a new dm channel
    direct_channel = member.dm_channel
    await direct_channel.send(f"Farewell {member.name}! We hope you polished some skills during your time with us.")
    return None

#listen for user messages
@client.event
async def on_message(message):
    #checks for admin priviledge, returns True if user sending message is admin
    def user_admin_test(message):
        #obtain a set of the names of the user roles
        user_roles = set()
        for role in message.author.roles:
            user_roles.update(set([role.name])) #sets implemented with hash tables-speeds program up
            return "Admin" in user_roles

    #checks message for any mentions of lemon, returns true if lemon mentioned
    def lemon_mention(message):
        #Determine if LEMON is mentioned via role id or user id
        mentioned = False
        for role in message.role_mentions:
            if 980727200045219894 == role.id:   #lemon's role id
                mentioned = True
        for mention in message.mentions:
            if mention.id == 823964022071754752: #lemon's user id
                mentioned = True
        return mentioned

    #checks if the message contains attachments and returns true if it does
    def has_attachements(message):
        if len(message.attachments)!=0:
            return True

    if str(message.channel.type) != "private":
        channel = str(message.channel.name) #get channel name

    #gather string reps of information about the message
    message.content.lower()
    username = str(message.author).split("#")[0] #remove discriminator
    user_message = str(message.content) #get the message sent

    # do not repeat events when the bot is message sender
    if message.author == client.user:
        return

    # determine if LEMON is being used for ModMail interactions
    if str(message.channel.type) == "private":
        mod_mail_channel = discord.utils.get(client.get_all_channels(), name="mod-mail") #get the mod mail channel from input
        #check for attachments
        if has_attachements: #this allows submissions of files for analysis
            await mod_mail_channel.send(f"{username} attached:")
            for file in message.attachments:
                await mod_mail_channel.send(file.url)
            return None


        else:
            await mod_mail_channel.send(f"{username} submitted: {user_message}")
            return None

    #determine if msg is a response to modmail
    elif channel == "mod-mail" and len(message.mentions)==1:
        member_obj = message.mentions[0]    #get user mentioned
        #check for file responses:
        if has_attachements:
            for file in message.attachments:
                await member_obj.send(f"Moderator {username} has replied with a file:")
                await member_obj.send(file.url)
            return None
        else:
            pos = message.content.index(" ")    #get everything after mention
            mod_message = user_message[pos:]    #modify the string to not have a mention
            await member_obj.send(f"{username} responded to your mod-mail: {mod_message}")
            return None

    #if user is sending a greeting, greet the user back with a help cmd
    if channel == "lemon-test_grounds" and lemon_mention:
        await message.channel.send(f"Salutations {username}. For my help: please type /lemonhelp")
        return None

    #lemonhelp menu
    if user_message == "/lemonhelp":
        await message.channel.send(f"Hello {username}, my current supported commands are: {command_names}. You can also PM me to send a ModMail message for the Q/A board")
        return None

    #online resource urls lookup
    if user_message.startswith("/resources"):
        tokens = user_message.split()   #split string at whitespaces
        #remove the /resources...
        tokens.pop(0)
        for token in tokens:
            token = token.upper()   #uppercase the keys
            try:
                accessed = manuals[token]   #access the dictionary at the key if the key exists
            except:
                await message.channel.send(f"Sorry {username}, {token} was not a key in our resource table. :(")
            else:
                #access the resource tuple stored at the key
                for url in accessed:
                    await message.channel.send(f"{url}")
        return None

    """
    Below this point is admin-only commands
    """
    #admin command to clean current text channel
    if user_message == "/purge" and user_admin_test and channel != "ddlc-dump":
        await message.channel.purge(limit=100)
        print(f"Purging of {channel} for 100 messages completed succsessfully")
        return None
    else:
        await message.channel.send(f"Sorry {username}, you have insufficient permissions to use this command!")
        return None

#notify machine that LEMON has disconnected during runtime
@client.event
async def on_disconnect():
    print(f"{client.user} has gone offline!")

#Runtime of bot:
client.run(token)

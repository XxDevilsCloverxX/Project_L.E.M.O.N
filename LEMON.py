"""
This is a discord bot created by students of Texas Tech University's
Tech Robotics Association to aid with the growth of the Texas Robotics scenes
"""
import discord  #bot commands and API
import os   #for the machine hosting LEMON
from dotenv import load_dotenv  #importing .env from host machine
from time import sleep  #call the machine to wait before performing a bot action
import csv  #opening separate csv files to access data

#import .env secrets
load_dotenv()

#init some variables for L.E.M.O.N
client = discord.Client() #send request to Discord API
token = os.getenv('TOKEN')  #get and init the token

"""
This is a global declaration block of variables that can be used
during LEMON's runtime...must be updated manually as games are released
"""
command_names = set(("/lemonhelp","/purge","/resources")) #set of command names LEMON users can access, function names are unique
manuals = {
"FTC": tuple(["https://www.firstinspires.org/sites/default/files/uploads/resource_library/ftc/game-manual-part-1-traditional-events.pdf", "https://www.firstinspires.org/sites/default/files/uploads/resource_library/ftc/game-manual-part-2-traditional.pdf"]),
"GEAR": tuple(["https://www.youtube.com/watch?v=tXWykG-8_Mw&list=PLJR32U_dICxeLXuzJeBRt3xAuo1TEZHdZ"]),
"VOLUNTEER": tuple(["https://www.firstinspires.org/resource-library/ftc/volunteer-resources"]),
"PROGRAMMING": tuple(["https://www.firstinspires.org/resource-library/ftc/technology-information-and-resources"]),
"FLL":tuple(["https://www.youtube.com/watch?v=tXWykG-8_Mw&list=PLJR32U_dICxeLXuzJeBRt3xAuo1TEZHdZ"]),
"MENTORSHIP": tuple(["https://www.techroboticsassociation.org/", "https://info.firstinspires.org/mentor-network"])
}   #dictionary containing online resource urls for the games, possibly .txts in the future
slurs = set() #set of unique words that will be used for lookups to prevent misbehavior

#open a csv and store the data as a set:
with open('Terms-to-Block.csv', 'r') as csvfile:
    #create csvreader
    csvreader = csv.reader(csvfile)
    #get the rows from the reader
    for row in csvreader:
        #strip the commas from the csv and access the words, update word to the set of slurs
        slurs.update([row[0].strip(',').lower()])

#initalize L.E.M.O.N
@client.event
async def on_ready():
    print(f"{client.user} successfully logged in.")

#greet a new memeber
@client.event
async def on_member_join(member):
    if member.dm_channel == None:
        await member.create_dm()   #create a new dm channel
    direct_channel = member.dm_channel
    await direct_channel.send(f"Salutations {member.name}! I am L.E.M.O.N, responsible for aiding everyone in the guild. Enjoy your stay! And feel free to check my open-source repo at: {None}")
    return None

#ping a departing member in private that we appreciate their time here
@client.event
async def on_member_remove(member):
    if member.dm_channel == None:
        await member.create_dm()   #create a new dm channel
    direct_channel = member.dm_channel
    await direct_channel.send(f"Farewell {member.name}! We hope you polished some skills during your time with us.")
    return None

#listen for user messages
@client.event
async def on_message(message):
    """
    Anything in this upper block of code executes on all
    Messages in Guild Channels L.E.M.O.N is allowed to see
    """
    # do not run scripts on message when the L.E.M.O.N is message sender
    if message.author == client.user:
        return None

    #copy the original message for usage with mod-mail submissions
    full_message = str(message.content)

    #lowercase the contents of the message
    message.content.lower()

    #returns True if message contained any slurs in our hash
    def contained_slurs(usermessage):
        contains = False
        #detect any slurs the message may contain
        for word in usermessage:
            for substring in slurs:
                if substring in word:
                    contains = True
        return contains

    #split the string to a list of it's parts (sepearated by spaces)
    user_message = str(message.content).split()
    #gather string representation of author without discriminator
    username = str(message.author).split("#")[0]

    #get slurs out of message view if not DM channel
    containment = contained_slurs(user_message)
    if containment and not str(message.channel.type) == "private":
        await message.channel.purge(limit=1)
        await message.channel.send(f"{username}, please watch your use of language!")
        #stop processing message request
        return None

    #if no slurs were detected, extract the command
    user_command = user_message.pop(0)

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
        return False

    #confirm that tokens were passed to the message:
    def has_tokens(msg):
        if len(msg)!=0:
            return True
        else:
            return False

    # determine if LEMON is being used for ModMail interactions
    if str(message.channel.type) == "private":
        mod_mail_channel = discord.utils.get(client.get_all_channels(), name="mod-mail") #get the mod mail channel from input
        #check for attachments
        if has_attachements(message): #this allows submissions of files for analysis
            await mod_mail_channel.send(f"{username} attached:")
            for file in message.attachments:
                await mod_mail_channel.send(file.url)
            return None

        else:
            #confirm that the message does not contain slurs that would otherwise be posted to mod-mail
            if not containment:
                await mod_mail_channel.send(f"{username} submitted: {full_message}")
            else:
                await message.channel.send(f"Sorry {username}! The message contained a potential slur and was not submitted to the mod-mail!")
            return None

    #determine if msg is a response to modmail
    elif str(message.channel.name) == "mod-mail" and len(message.mentions)!=0:
            member_obj = message.mentions[0] #get user mentioned
            #check for file responses:
            if has_attachements(message):
                for file in message.attachments:
                    await member_obj.send(f"Moderator {username} has replied with a file:")
                    await member_obj.send(file.url)
                return None

            else:
                pos = message.content.index(" ")    #get everything after mention
                mod_message = user_message[pos:]    #modify the string to not have a mention
                await member_obj.send(f"{username} responded to your mod-mail: {mod_message}")
                return None

    #confirm that the message is a valid command before checking command operations
    if user_command in command_names or lemon_mention(message):

        #if user is mentions lemon, greet user and offer help
        if lemon_mention(message):
                await message.channel.send(f"Salutations {username}. For my help: please type /lemonhelp")
                return None

        #lemonhelp menu
        if user_command == "/lemonhelp":
                await message.channel.send(f"Hello {username}, my current supported commands are: {command_names}. You can also PM me to send a ModMail message for the mod-mail channel.")
                return None

        #/resource command accessible to @everyone
        if user_command == "/resources":
                #confirm that user passed tokens:
                if not has_tokens(user_message):
                    await message.channel.send("You have tried to use /resources with no topics! try '/resources [topics]' (a spaced list of topics without brackets or commas)")
                    await message.channel.send(f"A list of supported topics includes: {manuals.keys()}")
                    return None
                else:
                    for token in user_message:
                        token = token.upper()   #uppercase the tokens
                        try:
                            accessed = manuals[token]   #access the dictionary at the key if the key exists
                        except:
                            await message.channel.send(f"Sorry {username}, {token} was not a key in our resource table. :(")
                        else:
                            #access the resource tuple stored at the key
                            for url in accessed:
                                await message.channel.send(f"{url}")
                                sleep(1)   #wait 1 second before message sends so links have time to embed
                    return None

        """
        Below this point is admin-only commands
        """
        #admin command to clean current text channel for 'arg' messages
        if user_command == "/purge" and user_admin_test(message):
            #confirm that a token is passed:
            if not has_tokens(user_message):
                    await message.channel.send("ERROR: /purge takes integer argument but None was given. try /purge (int)")
                    return None

                #a token was passed
            else:
                    #try to convert the argument to a integer
                    try:
                        arg = int(user_message[0])  #user_message at the first index should be the integer passed with the /purge command
                    except:
                        await message.channel.send(f"argument '{user_message[0]}' not convertible to int type.")
                        return None
                    else:
                        await message.channel.purge(limit=arg)
                        print(f"Purging of {message.channel.name} history for {arg} messages completed succsessfully")
                        return None
        elif user_command == "/purge" and not user_admin_test(message):
                await message.channel.send(f"Sorry {username}, you have insufficient permissions to use /purge command!")
                return None

    #below this else statement will execute on every non-command!
    else:
            return None

#notify machine that LEMON has disconnected during runtime
@client.event
async def on_disconnect():
    print(f"{client.user} has gone offline!")

#Runtime of bot:
client.run(token)

#Subject to change:
#Luxury
#Experimental
#Manager-bot
#Offering
#Nerds some assistance

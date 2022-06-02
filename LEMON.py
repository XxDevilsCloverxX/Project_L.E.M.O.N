"""
This is the pilot script for the Discord bot created by students of Texas Tech University's
Tech Robotics Association to aid with the growth of the Texas Robotics scenes
"""
import discord  #bot commands and API
import os   #for the machine hosting LEMON
from dotenv import load_dotenv  #imports secrets from the enviornment
from time import sleep  #call the machine to wait before performing a bot action

from slur_extraction import slurs   #imports a set of all the slurs to check for
import message_handling as msg_handle #import the message handling functions
from resources import manuals   #resource dictionary for /resources command

#import .env secrets
load_dotenv()

#init some variables for L.E.M.O.N
client = discord.Client() #send request to Discord API
token = os.getenv('TOKEN')  #get and init the token
#specify intents
discord.Intents.all()

"""
This is a global variable declaration block that can be used
during LEMON's runtime...commands are hard-coded in
"""
command_names = set(("/lemonhelp","/purge","/resources")) #set of command names LEMON users can access, function names are unique
lemon_url = "https://github.com/XxDevilsCloverxX/Project_L.E.M.O.N"

#initalize L.E.M.O.N
@client.event
async def on_ready():
    #notify clean login
    print(f"{client.user} successfully logged in.")

    #fetch guild roles
    roles = client.guilds[0].roles[::-1]
    #change 3 to the top n roles that have admin priviledge
    global admin_roles
    admin_roles = roles[:3]

    #obtain special channels
    global channel_mod_mails
    channel_mod_mails = discord.utils.find(lambda ch: "mail" in ch.name.lower() and "mail" in ch.name.lower(), client.guilds[0].channels) #get a channel with mod and mail in the name
    global channel_joins
    channel_joins = discord.utils.find(lambda ch: "join" in ch.name.lower(), client.guilds[0].channels) #find a channel with join in name

    try:
        print(f"\nImportant:\n{channel_mod_mails.name} set as mod_mail channel\n{channel_joins.name} set as joins channel.\nIf this is a mistake, terminate the hosting session.")
    except:
        print(f"\nIt appears that mod-mail or joins channel are not enabled on your server. To enable these features in the program, create a mod-mail channel whose name contains 'mod' and 'mail', and a join channel containing 'join' in the name")

    #obtain LEMON's role
    global lemon_id
    lemon_id = discord.utils.find(lambda mm: "lemon" in mm.name.lower(), roles)
    print(f"{lemon_id.name}: {lemon_id.id}")

#greet a new memeber
@client.event
async def on_member_join(member):
    print(f"{member.name} has joined {client.guilds[0].name}!")
    await member.send(f"Salutations {member.name}! I am L.E.M.O.N, responsible for aiding everyone in {member.guild.name}. Enjoy your stay! And feel free to check my open-source repo at: {lemon_url}")
    await channel_joins.send(f"Salutations {member.name}, welcome to {channel_joins.guild.name}!")

#ping a departing member in private that we appreciate their time here
@client.event
async def on_member_remove(member):
    print(f"{member.name} has left {client.guilds[0].name}!")
    await member.send(f"Farewell, {member.name}! {client.guilds[0].name} wishes you success and prosperity!")
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

    #a function from message_handling, returns an ordered tuple of information extracted from message_obj
    extraction = msg_handle.message_obj_analysis(message)  #extraction: (str: username, str: original message_obj, str: stripped message_obj, list: [message_obj tokens])

    #get slurs out of message view if not DM channel, uses the tokens and stripped message
    containment = msg_handle.contained_slurs(extraction[-1], slurs) or msg_handle.contained_slurs([[2]], slurs)

    if containment and not str(message.channel.type) == "private":
        await message.channel.purge(limit=1)
        await message.channel.send(f"{extraction[0]}, please watch your language!")
        #stop processing message request
        return None

    #if no slurs were detected, extract the command
    try:
        user_command = extraction[-1].pop(0)
    except:
        #user sent an attachment that didn't contain a message
        if str(message.channel.type) == "private":
            await message.channel.send(f"Please include text with your attachment {extraction[0]}.")
    #run this if any content was in the message
    else:

        # determine if LEMON is being used for ModMail interactions
        if str(message.channel.type) == "private":
            if channel_mod_mails.type != None:
                #check for attachments
                if has_attachements(message): #this allows submissions of files for analysis
                    await channel_mod_mails.send(f"{extraction[0]} attached:")
                    for file in message.attachments:
                        await channel_mod_mails.send(file.url)

                #confirm that the message does not contain slurs that would otherwise be posted to mod-mail
                if not containment:
                    await channel_mod_mails.send(f"{extraction[0]} submitted: {extraction[1]}")
                else:
                    await message.channel.send(f"Sorry {extraction[0]}! Your message potentially contained a slur and was not submitted to {channel_mod_mails.name}! Attachments still processed, so you should just resend your message.")
                return None
            else:
                await message.channel.send(f"Sorry {extraction[0]}, it appears this server does not have a mod-mail channel established. Please ping mods instead.")

        #determine if msg is a response to modmail
        elif str(message.channel.name) == channel_mod_mails.name and len(message.mentions)!=0:
                member_obj = message.mentions[0] #get user mentioned
                #check for file responses:
                if has_attachements(message):
                    for file in message.attachments:
                        await member_obj.send(f"Moderator {extraction[0]} has replied with a file:")
                        await member_obj.send(file.url)
                    return None

                else:
                    pos = message.content.index(" ")    #get everything after mention
                    mod_message = extraction[-1][pos:]    #modify the string to not have a mention
                    await member_obj.send(f"{extraction[0]} responded to your mod-mail: {mod_message}")
                    return None

        #confirm that the message is a valid command before checking command operations
        if user_command in command_names or msg_handle.lemon_mention(message, lemon_id.id):

            #if user is mentions lemon, greet user and offer help
            if msg_handle.lemon_mention(message, lemon_id.id):
                    await message.channel.send(f"Salutations {extraction[0]}. For my help: please type /lemonhelp")
                    return None

            #lemonhelp menu
            if user_command == "/lemonhelp":
                    await message.channel.send(f"Hello {extraction[0]}, my current supported commands are: {command_names}. You can also PM me to send a ModMail message for the mod-mail channel.")
                    return None

            #/resource command accessible to @everyone
            if user_command == "/resources":
                    #confirm that user passed tokens:
                    if not msg_handle.has_tokens(extraction[-1]):
                        await message.channel.send("You have tried to use /resources with no topics! try '/resources [topics]' (a spaced list of topics without brackets or commas)")
                        await message.channel.send(f"A list of supported topics includes: {manuals.keys()}")
                        return None
                    else:
                        for token in extraction[-1]:
                            token = token.upper()   #uppercase the tokens
                            try:
                                accessed = manuals[token]   #access the dictionary at the key if the key exists
                            except:
                                await message.channel.send(f"Sorry {extraction[0]}, {token} was not a key in our resource table. :(")
                            else:
                                #access the resource tuple stored at the key
                                for url in accessed:
                                    await message.channel.send(f"{url}")
                                    sleep(2)   #wait 2 seconds before message sends so links have time to process
                        return None

            """
            Below this point is admin-only commands
            """
            #admin command to clean current text channel for 'arg' messages
            if user_command == "/purge" and msg_handle.user_admin_test(message, admin_roles):
                #confirm that a token is passed:
                if not msg_handle.has_tokens(extraction[-1]):
                        await message.channel.send("ERROR: /purge takes integer argument but None was given. try /purge (int)")
                        return None

                    #a token was passed
                else:
                        #try to convert the argument to a integer
                        try:
                            arg = int(extraction[-1][0])  #user_message at the first index should be the integer passed with the /purge command
                        except:
                            await message.channel.send(f"argument '{extraction[-1][0]}' not convertible to int type.")
                            return None
                        else:
                            await message.channel.purge(limit=arg+1)    #also removes the /purge call
                            print(f"Purging of {message.channel.name} history for {arg} messages completed succsessfully")
                            return None
            elif user_command == "/purge" and not msg_handle.user_admin_test(message, admin_roles):
                    await message.channel.send(f"Sorry {extraction[0]}, you have insufficient permissions to use /purge command!")
                    return None

        #below this else statement will execute on every non-command!
        else:
                return None

#notify machine that LEMON has disconnected during runtime
@client.event
async def on_disconnect():
    print(f"{client.user} has gone offline!")

@client.event
async def on_message_edit(before, after):
    """
    Not much to do here besides prevent editing in slurs
    """
    #a function from message_handling, returns an ordered tuple of information extracted from message_obj
    extraction = msg_handle.message_obj_analysis(after)  #extraction: (str: username, str: original message_obj, str: stripped message_obj, list: [message_obj tokens])

    #like before, test for slurs and purge the channel as needed
    containment = msg_handle.contained_slurs(extraction[-1]) or msg_handle.contained_slurs([extraction[2]])
    if containment and not str(after.channel.type) == "private":
        await after.channel.purge(limit=1)
        await after.channel.send(f"{extraction[0]}, please watch your language!")
        #stop processing message request
        return None

#Runtime of bot:
client.run(token)

#Subject to change:
#Logistics
#Experiment
#Made with
#Organized and
#Nifty code

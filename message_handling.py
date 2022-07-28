"""
This is the script housing commands that handle message_obj operations
that LEMON uses to analyze submissions to Guild Channels LEMON can
see.
"""

import discord  #Discord API and Objects

# message_obj information extraction, returns a tuple of strings: (str: username,
# str: original message_obj, str: stripped message_obj, list: [message_obj tokens])
def message_obj_analysis(message_obj):

    #copy the original message_obj for usage with mod-mail submissions
    original_msg = str(message_obj.content)

    #lowercase the contents of the message_obj
    message_obj.content = message_obj.content.lower()

    #collect a copy of the message_obj with no space, or other symbol, that fools censor checker
    stripped = message_obj.content.replace(" ","").replace("-","").replace("_","").replace("|","").replace(":","").replace(";","").replace("~","").replace("=","").replace("+","").replace("*","").replace(".", "")

    #split the string into a list of it's parts (sepearated by spaces)
    user_message_obj = str(message_obj.content).split()

    #gather string representation of author without discriminator
    username = str(message_obj.author).split("#")[0]

    #create a tuple of these objects and return it
    return (username, original_msg, stripped, user_message_obj)

#checks for admin priviledge of message author, returns True if user sending message_obj is admin
def user_admin_test(message_obj, admin_roles):
    assert type(admin_roles) == list, "Error: admin_roles must be a list object!"
    #using the list of author roles, check if the author roles are in admin_table
    for role in message_obj.author.roles:
        if role in admin_roles:
            return True
    return False

#checks message_obj for any mentions of lemon, returns true if LEMON is mentioned via role or username
def lemon_mention(message_obj, role_id):
    assert type(role_id) == int, "ERROR: role_id is not integer object!"
    #Determine if LEMON is mentioned via role id or user id
    mentioned = False
    for role in message_obj.role_mentions:
        if role_id == role.id:   #lemon's role id
            mentioned = True
    for mention in message_obj.mentions:
        if mention.id == 823964022071754752: #lemon's unique user id
            mentioned = True

    return mentioned

#checks if the message_obj contains attachments and returns true if it does
def has_attachements(message_obj):
    if len(message_obj.attachments)!=0:
        return True
    return False

#confirm that tokens were passed to the message_obj: returns true if user_message contained tokens, used after command extraction in LEMON.py
def has_tokens(split_message):
    assert type(split_message) == list, "Message must be a list type to contain tokens!"
    if len(split_message)!=0:
        return True
    else:
        return False

import os
import time

import discord

from functions import *
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='qr ')

@bot.command(name='ok', help = "haha huhu")
async def ok(ctx):
    await ctx.send("ok")

fetchHelp = "1) Do '-q' to make groovy display the queue.\n" + \
            "2) Go to the first page of the queue by reacting.\n" +\
            "3) When at first page, do 'qr fetch' and then wait for the bot to say 'ok'\n"+ \
            "4) start going forward until the bot says 'ok', do this for all pagesuntil you reach the last page.\n" +\
            "5) The bot will automatically return a list of songs.\n"+\
            "CAUTION: Be sure noone texts on the chat during that time!"

#very bad implementaion, code just works tho

@bot.command(name='fetch', help = fetchHelp)
async def ok(ctx):
    queuePages = ["sample"]
    messages = await ctx.channel.history(limit=2).flatten()         # list of last 2 messages
    queueMessage = messages[1]                                      # getting the second last message (the queue)
    userName = messages[0].author
    guildName = messages[0].guild
    queueMessageID = queueMessage.id                                # ID of the queue message

    """
    We check every 1/2 second if the queueMessage is different from the last message in queuePages. Obviously, for the first iteration ...
    ... the message would be different so it would be appended. Then the bot would say "ok" prompting you to press "Next" so the ...
    ... message changes (but the ID remains the same). Now, after pressing "Next", the message would be different from the last ...
    ... element of queuePages, so we append. This implementation is very deliberate.
    """

    pageNumber = 1
    while True:
        time.sleep(0.5)

        queueMessage = await ctx.fetch_message(queueMessageID)
        queueMessageContent = queueMessage.content                       # fetch msg
        #print(queueMessageContent)
        list = queueMessageContent.split("\n")
        # print(list)
        list.pop()              # removing the last element ("```")
        list.pop(0)             # removing the first element ("```nim")
        lastSentence = list[-1].strip()     # Important as we check if we have reached the end or not
        list.pop()                          # removing the last element
        itemIndexWhereLeftIs = None                    # this is to get rid of the "left" thing
        for item in list:
            if "current track" in item:
                list.remove(item)
        for item in list:
            strippedItem = item.strip()
            if strippedItem[-4:] == "left":
                itemIndexWhereLeftIs = list.index(item)

        if type(itemIndexWhereLeftIs) == int:
            list[itemIndexWhereLeftIs] = list[itemIndexWhereLeftIs].strip().rstrip("left")  # removing the "left"
        formattedMessage = "\n".join(list).strip()


        if formattedMessage == queuePages[-1]:  # if the current message is same as last, we dont add this in the queuepages
            continue
        else:
            # See if this page is the last page, if yes, break

            queuePages.append(formattedMessage)
            await ctx.send(pageNumber)
            pageNumber += 1
            if lastSentence == "This is the end of the queue!":
                c = "All " + str(pageNumber) + " pages have been fetched!"
                await ctx.send(c)
                break
    # getting rid of that "sample"
    queuePages.pop(0)


    # printing to console the final parsed list.
    for item in queuePages:
        print(item)
    queueFileName = "queueFile_" + str(userName) + str(guildName) + ".txt"
    queueFile = open(queueFileName, "w")
    for item in queuePages:
        queueFile.write(item)
        queueFile.write("\n")
    queueFile.close()
    await ctx.send(file=discord.File(queueFileName))
    os.remove(queueFileName)

    #embeds = [embed for embed in message.embeds]
    #while embeds:
    #    print(embeds.pop().to_dict())
    #await ctx.send()

bot.run(TOKEN)
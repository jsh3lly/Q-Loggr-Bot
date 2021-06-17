import os
import time

import discord
from discord.ext import commands
from dotenv import load_dotenv

from functions import *
import yt

from collections import OrderedDict

def main():
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
    async def fetch(ctx):
        listOfAllTracks = ["sample"]
        lastTwoMessages = await ctx.channel.history(limit=2).flatten()                  # currentPgListOfAllTracks of last 2 lastTwoMessages
        currentPgQueueMessage = lastTwoMessages[1]                                      # getting the second last message (the queue)
        lastMessage = lastTwoMessages[0]                                                # getting the last message ("qr fetch")
        userName = lastMessage.author                                                   # user who invoked the command
        guildName = lastMessage.guild                                                   # server on which the command was invoked
        queueMessageID = currentPgQueueMessage.id                                       # ID of the queue message

        """
        We check every 1/2 second if the currentPgQueueMessage is different from the last message in listOfAllTracks. Obviously, for the first iteration ...
        ... the message would be different so it would be appended. Then the bot would say "ok" prompting you to press "Next" so the ...
        ... message changes (but the ID remains the same). Now, after pressing "Next", the message would be different from the last ...
        ... element of listOfAllTracks, so we append. This implementation is very deliberate.
        """

        pageNumber = 1
        while True:
            time.sleep(0.5)
            currentPgQueueMessage = await ctx.fetch_message(queueMessageID)
            currentPgQueueMessageContent = currentPgQueueMessage.content                       # fetch msg
            #print(currentPgQueueMessageContent)
            currentPgListOfAllTracks = currentPgQueueMessageContent.split("\n")
            # print(currentPgListOfAllTracks)
            currentPgListOfAllTracks.pop()              # removing the last element ("```")
            currentPgListOfAllTracks.pop(0)             # removing the first element ("```nim")
            lastSentence = currentPgListOfAllTracks[-1].strip()     # Important as we check if we have reached the end or not
            currentPgListOfAllTracks.pop()                          # removing the last element
            itemIndexWhereLeftIs = None                    # this variable is to get rid of the "left" thing
            for item in currentPgListOfAllTracks:
                if "current track" in item:
                    currentPgListOfAllTracks.remove(item)
            for item in currentPgListOfAllTracks:
                strippedItem = item.strip()
                if strippedItem[-4:] == "left":
                    itemIndexWhereLeftIs = currentPgListOfAllTracks.index(item)

            if type(itemIndexWhereLeftIs) == int:
                currentPgListOfAllTracks[itemIndexWhereLeftIs] = currentPgListOfAllTracks[itemIndexWhereLeftIs].strip().rstrip("left")  # removing the "left"
            formattedMessage = "\n".join(currentPgListOfAllTracks).strip()


            if formattedMessage == listOfAllTracks[-1]:  # if the current message is same as last, we dont add this in the queuepages
                continue
            else:
                # See if this page is the last page, if yes, break

                listOfAllTracks.append(formattedMessage)
                await ctx.send(pageNumber)
                pageNumber += 1
                if lastSentence == "This is the end of the queue!":
                    c = "All " + str(pageNumber) + " pages have been fetched!"
                    await ctx.send(c)
                    break
        # getting rid of that "sample"
        listOfAllTracks.pop(0)

        # As of now, the listOfAllTracks is a list of "blocks" of tracks, rather than actual tracks, has inconsistent whitespaces,  and may have some duplicates

        # Flattening the list out:
        newListOfAllTracks = []
        for block in listOfAllTracks:
            tracks = block.split("\n")
            for track in tracks:
                newListOfAllTracks.append(track)

        listOfAllTracks = newListOfAllTracks
        del newListOfAllTracks

        # Consistent whitespaces:
        for i in range(len(listOfAllTracks)):
            strippedItem = listOfAllTracks[i].strip()
            listOfAllTracks[i] = strippedItem


        # Removing duplicates
        listOfAllTracks = OrderedDict.fromkeys(listOfAllTracks)
        listOfAllTracks = list(listOfAllTracks)

        # printing to console the final parsed currentPgListOfAllTracks.
        queueFileName = "queueFile_" + str(userName) + str(guildName) + ".txt"
        queueFile = open(queueFileName, "w")
        for item in listOfAllTracks:
            queueFile.write(item)
            queueFile.write("\n")
        queueFile.close()
        await ctx.send(file=discord.File(queueFileName))
        os.remove(queueFileName)

    @bot.command(name='makepl', help = "in progress")
    async def makepl(ctx, playlistName):
        lastTwoMessages = await ctx.channel.history(limit=2).flatten()  # currentPgListOfAllTracks of last 2 lastTwoMessages
        queueFile = lastTwoMessages[1]
        textFileAttachment = queueFile.attachments[0]
        messageFile = await textFileAttachment.read()
        messageContent = messageFile.decode("utf-8").strip()


        listOfListOfTrackInfo = splitQueueFile(messageContent)

        print(listOfListOfTrackInfo)

        playlistURL = yt.main(playlistName, listOfListOfTrackInfo)
        message = "The playlist URL is: " + playlistURL
        await ctx.send(message)

    bot.run(TOKEN)

if __name__ == '__main__':
    main()
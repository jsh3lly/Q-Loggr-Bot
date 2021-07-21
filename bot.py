import os
import time

import discord
from discord.ext import commands
from dotenv import load_dotenv

from functions import *

from collections import OrderedDict

#----------yt stuff----------
import os

from google_auth_oauthlib.flow import Flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]


from io import StringIO
import sys
#----------------------------

def main():
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')

    bot = commands.Bot(command_prefix='qr ')

    # @bot.command(name='fetchemo')
    # async def fetchry(ctx):
    #     lastTwoMessages = await ctx.channel.history(limit=2).flatten()                  # currentPgListOfAllTracks of last 2 lastTwoMessages
    #     currentPgQueueMessage = lastTwoMessages[1]                                      # getting the second last message (the queue)
    #     lastMessage = lastTwoMessages[0]                                                # getting the last message ("qr fetch")

    @bot.command(name='save')
    async def save(ctx):
        message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        user = ctx.message.author
        songLink = message.embeds[0].description
        songLink = songLink.split("https")[1]
        songLink = songLink.split(")")[0]
        songLink = "https" + songLink
        await user.send(songLink)
        await ctx.message.add_reaction("👌")

    @bot.command(name='echoreply')
    async def echoreply(ctx):
        message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        await ctx.send(message.content)

    @bot.command(name='ok', help = "haha huhu")
    async def ok(ctx):
        await ctx.send("ok")

    fetchHelp = "1) Do '-q' to make groovy display the queue.\n" + \
                "2) Go to the first page of the queue by reacting.\n" + \
                "3) When at first page, do 'qr fetch' and then wait for the bot to say 'ok'\n"+ \
                "4) start going forward until the bot says 'ok', do this for all pagesuntil you reach the last page.\n" + \
                "5) The bot will automatically return a list of songs.\n"+ \
                "CAUTION: Be sure noone texts on the chat during that time!"

    #very bad implementaion, code just works tho
    @bot.command(name='fetch', help = fetchHelp)
    async def fetch(ctx):
        listOfAllTracks = ["sample"]
        """lastTwoMessages = await ctx.channel.history(limit=2).flatten()                  # currentPgListOfAllTracks of last 2 lastTwoMessages
        currentPgQueueMessage = lastTwoMessages[1]                                      # getting the second last message (the queue)"""

        currentPgQueueMessage = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        lastMessage = ctx.message                                                       # getting the last message ("qr fetch")
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
            cancelMessage = await ctx.channel.history(limit=1).flatten()
            if cancelMessage[0].content == "cancel":
                await ctx.send("Cancelling request")
                return 0
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
        queueFile = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        textFileAttachment = queueFile.attachments[0]
        messageFile = await textFileAttachment.read()
        messageContent = messageFile.decode("utf-8").strip()


        listOfListOfTrackInfo = splitQueueFile(messageContent)

        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "google-credentials.json"

        # Get credentials and create an API client

        flow = Flow.from_client_secrets_file(client_secrets_file, scopes, redirect_uri='urn:ietf:wg:oauth:2.0:oob')

        auth_url = flow.authorization_url()
        await ctx.send('Please go to this URL: {}'.format(auth_url))
        await ctx.send('After going to the URL, enter here the code u get and then the bot will proceed further, DO NOT ENTER ANYTHING ELSE OR THE BOT WILL BREAK!')

        while True:
            cancelMessage = await ctx.channel.history(limit=1).flatten()
            if cancelMessage[0].content == "cancel":
                await ctx.send("Cancelling request")
                return 0
            time.sleep(0.5)
            codeMessage = await ctx.channel.history(limit=1).flatten()
            codeMessage = codeMessage[0]
            if codeMessage.author != ctx.author:
                continue
            codeMessage = codeMessage.content.strip()
            break

        flow.fetch_token(code=codeMessage)
        credentials = flow.credentials

        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)


        # ============= Making the playlist =============
        request = youtube.playlists().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": playlistName,
                    "description": "This is a sample playlist description.",
                    "tags": [
                        "sample playlist",
                        "API call"
                    ],
                    "defaultLanguage": "en"
                },
                "status": {
                    "privacyStatus": "public"
                }
            }
        )
        response = request.execute()

        playlistID = response.get('id')

        # ======== Searching and adding the songs to the playlist =========

        for listOfTrackinfo in listOfListOfTrackInfo[::-1]:   # Reversing the list cuz yt displays videos in "date added (newest)" form

            # ======== Searching ========
            songNameAndArtist = listOfTrackinfo[1]

            request = youtube.search().list(
                part="snippet",
                maxResults=1,
                q=songNameAndArtist
            )

            response = request.execute()
            videoID = response.get('items')[0].get('id').get('videoId')

            # ======== Adding to playlist ========
            request = youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlistID,
                        "position": 0,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": videoID
                        }
                    }
                }
            )

            response = request.execute()

        playlistURL = "https://www.youtube.com/playlist?list=" + playlistID

        message = "The playlist URL is: " + playlistURL
        await ctx.send(message)

    bot.run(TOKEN)
if __name__ == '__main__':
    main()
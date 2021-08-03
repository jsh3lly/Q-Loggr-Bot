import os
import time
import ipinfo
import discord, asyncio
from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType
from dotenv import load_dotenv
from functions import *
from collections import OrderedDict


#----------yt stuff----------

from google_auth_oauthlib.flow import Flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]


#----------embeds for help----------
embedHelp = discord.Embed(
    title = "Q-Loggr Help Portal", 
    description = '''Please navigate to the help page for your desired command!\n 
    For quick reference, here are the available commands :\n 
    1. **qr save**  : Like a song and want to save it to your DMs? `qr save` it right away!
    2. **qr fetch** : The queue has absolute bangers and you wanna queue songs the same way again ? `qr fetch` is at your rescue!
    3. **qr makepl <playlistname>**: A convenient method to save the queue as a YouTube playlist. Do `qr makepl <playlistname>` to generate a playlist.\n'''
     
)
embedSave = discord.Embed(
    title = "Yeeting a song to your DMs",
    description = '''This can be achieved via `qr save`.
    **Steps:**
    1. Do `-np` (for Groovy) or `.np` (for Hydra) to get the song which is currently playing
    2. Reply to the message with `qr save`
    3. Q-Loggr sends the song url to your DMs \n
    **For this to work you need to have `Allow direct messages from server members` toggled on.**'''

)
embedFetch = discord.Embed(
    title = "I can't get enough of this queue!",
    description = '''`qr fetch` generates a text file of the current queue.
    **Steps:**
    1. Do `-q` to get the queue.
    2. Go to the first page by reacting to `First` button.
    3. Reply to the message with `qr fetch`.
    4. Go forward using the `Next` button until you've reached the end of the queue.
    5. Q-Loggr sends the text file of the queue in the channel.'''
)
embedPlayl = discord.Embed(
    title = "This needs to be a YouTube playlist!",
    description = '''`qr makepl <PlaylistName>` generates a YouTube playlist based on the text file generated.
    **Steps:**
    1. Generate the text file first using `qr fetch`
    2. Reply to the generated text file with `qr makepl <PlaylistName>`
    3. Wait for the bot to send an authentication link.
    4. Sign-In using your Google Account to give permissions to the application to create a playlist.
    5. Q-Loggr sends the generated playlist URL in channel.
    **CAUTION !** `qr makepl` usage is limited to once a day for 65 songs or less.'''

)
embedWhere = discord.Embed(
    title = "Where is this bot hosted?",
    description = '''`qr where` provides basic information on Q-Loggr's current host and region details.
    **Steps:**
    1. Do qr where to access details.
    NOTE: This is supposed to be a utility command and spamming the command will lead to API ratelimit for ipinfo. '''
)

#Getting all embeds in a list
helpList = [embedHelp, embedSave, embedFetch, embedPlayl,embedWhere] 


#----------------------------

def main():
    load_dotenv()
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    IPINFO_TOKEN = os.getenv('IPINFO_TOKEN')

    bot = commands.Bot(command_prefix='qr ',help_command=None)
    DiscordComponents(bot)

    @bot.event
    async def on_ready():
        print('Logged in as')
        print(bot.user.name)
        print(bot.user.id)
        print('------')
        print(os.path.expanduser("~"))



    @bot.command(name='where')
    async def where(ctx):
        access_token = os.getenv('IPINFO_TOKEN')
        handler = ipinfo.getHandler(access_token)
        details = handler.getDetails()
        
        embed = discord.Embed(title="Server and Region Details for Q-Loggr", description="Know where the bot is hosted currently.",color=0x88EAFF) 
        embed.add_field(name="Organisation Name", value=details.org)
        try:
            embed.add_field(name="Host", value=details.hostname)
        except AttributeError:
            embed.add_field(name="Host", value="localhost")
        embed.add_field(name="City", value=details.city)
        embed.add_field(name="Country", value=details.country_name)
        embed.set_footer(text="Q-Loggr Utility")
        await ctx.send(embed=embed)


    @bot.command(name='save')
    async def save(ctx, messageSong = None):
        user = ctx.message.author
        if messageSong == None:
            message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            if ctx.message.reference.resolved.author.display_name == "Hydra":      #hydra
                songLink = message.embeds[0].url

            else:
                songLink = message.embeds[0].description
                songLink = songLink.split("https")[1]
                songLink = songLink.split(")")[0]
                songLink = "https" + songLink
            await user.send(songLink)

        else:
            await user.send(messageSong)
        await ctx.message.add_reaction("👌")

    
    @bot.command(name = "help")
    async def support(ctx):
        #Set a default embed first
        current = 0
        mainMessage = await ctx.reply(
            "**Support has arrived!**",
            embed = helpList[current],
            components = [
                [
                    Button(
                        label = "Prev",
                        id = "back",
                        style = ButtonStyle.blue
                    ),
                    Button(
                        label = f"Page {int(helpList.index(helpList[current])) + 1}/{len(helpList)}",
                        id = "cur",
                        style = ButtonStyle.grey,
                        disabled = True
                    ),
                    Button(
                        label = "Next",
                        id = "front",
                        style = ButtonStyle.blue
                    )
                ]
            ]
        )

        while True:
            #Try and except blocks to catch timeout and break
            try:
                interaction = await bot.wait_for(
                    "button_click",
                    check = lambda i: i.component.id in ["back", "front"],
                    timeout = 60                                                #60 seconds of inactivity
                )
                #Getting the right list index
                if interaction.component.id == "back":
                    current -= 1
                elif interaction.component.id == "front":
                    current += 1
                #If its out of index, go back to start / end
                if current == len(helpList):
                    current = 0
                elif current < 0:
                    current = len(helpList) - 1

                #Edit to new page + the center counter
                await interaction.respond(
                    type = InteractionType.UpdateMessage,
                    embed = helpList[current],
                    components = [ 
                        [
                            Button(
                                label = "Prev",
                                id = "back",
                                style = ButtonStyle.blue
                            ),
                            Button(
                                label = f"Page {int(helpList.index(helpList[current])) + 1}/{len(helpList)}",
                                id = "cur",
                                style = ButtonStyle.grey,
                                disabled = True
                            ),
                            Button(
                                label = "Next",
                                id = "front",
                                style = ButtonStyle.blue
                            )
                        ]
                    ]
                )
            except asyncio.TimeoutError:
                #Disable and get outta here
                await mainMessage.edit("*This interaction has expired now*",
                    components = [
                        [
                            Button(
                                label = "Prev",
                                id = "back",
                                style = ButtonStyle.blue,
                                disabled = True
                            ),
                            Button(
                                label = f"Page {int(helpList.index(helpList[current])) + 1}/{len(helpList)}",
                                id = "cur",
                                style = ButtonStyle.grey,
                                disabled = True
                            ),
                            Button(
                                label = "Next",
                                id = "front",
                                style = ButtonStyle.blue,
                                disabled = True
                            )
                        ]
                    ]
                )
                break

    #very bad implementaion, code just works tho
    @bot.command(name='fetch')
    async def fetch(ctx):
        listOfAllTracks = ["sample"]
        currentPgQueueMessage = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        lastMessage = ctx.message                                                       # getting the last message ("qr fetch")
        userName = lastMessage.author                                                   # user who invoked the command
        guildName = lastMessage.guild                                                   # server on which the command was invoked
        queueMessageID = currentPgQueueMessage.id                                       # ID of the queue message

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

        # Flattening the list out and removing whitespaces:
        newListOfAllTracks = []
        for block in listOfAllTracks:
            tracks = block.split("\n")
            for track in tracks:
                newListOfAllTracks.append(track.strip())

        listOfAllTracks = newListOfAllTracks
        del newListOfAllTracks

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

    @bot.command(name='makepl')
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
        await ctx.send('Please go to the following URL:\n {}'.format(auth_url[0]))
        replyToThisMessage = await ctx.send('After going to the URL, enter here the code u get and then the bot will proceed further, DO NOT ENTER ANYTHING ELSE OR THE BOT WILL BREAK!')

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
                    "description": "This is a playlist created by Q-Loggr. Star: https://github.com/StaticESC/Q-Loggr-Bot. Thank you.",
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

    bot.run(DISCORD_TOKEN)
if __name__ == '__main__':
    main()
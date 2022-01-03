import discord
# ----------embeds for help----------
embedHelp = discord.Embed(
    title="Q-Loggr Help Portal",
    description='''Please navigate to the help page for your desired command!
    For quick reference, here are the available commands \n''')
embedHelp.add_field(name='1. qr save  ',
                    value='Like a song and want to save it to your DMs? `qr save` it right away!')
embedHelp.add_field(name='2. qr fetch',
                    value='The queue has absolute bangers and you wanna queue songs the same way again ? `qr fetch` is at your rescue!')
embedHelp.add_field(name='3. qr makepl <playlistname> ',
                    value='A convenient method to save the queue as a YouTube playlist. Do `qr makepl <playlistname>` to generate a playlist.')
embedHelp.add_field(name='4. qr where', value='Returns bot hosting details.')


embedSave = discord.Embed(
    title="Yeeting a song to your DMs",
    description="This can be achieved via `qr save`.")
embedSave.add_field(name='Steps',value='''1. Do `-np` (for Groovy) or `.np` (for Hydra) to get the song which is currently playing
    2. Reply to the message with `qr save`
    3. Q-Loggr sends the song url to your DMs \n
    For this to work you need to have `Allow direct messages from server members` toggled on.'''
)
embedFetch = discord.Embed(
    title="I can't get enough of this queue!",
    description='''`qr fetch` generates a text file of the current queue.
    Steps
    1. Do `-q` to get the queue.
    2. Go to the first page by reacting to `First` button.
    3. Reply to the message with `qr fetch`.
    4. Go forward using the `Next` button until you've reached the end of the queue.
    5. Q-Loggr sends the text file of the queue in the channel.'''
)
embedPlayl = discord.Embed(
    title="This needs to be a YouTube playlist!",
    description='''`qr makepl <PlaylistName>` generates a YouTube playlist based on the text file generated.
    Steps
    1. Generate the text file first using `qr fetch`
    2. Reply to the generated text file with `qr makepl <PlaylistName>`
    3. Wait for the bot to send an authentication link in your DM Make sure `Allow Direct Messages from Server Members` IS TURNED ON.
    4. Sign-In using your Google Account to give permissions to the application to create a playlist.
    5. Q-Loggr sends the generated playlist URL in channel.
    CAUTION ! `qr makepl` usage is limited to once a day for 65 songs or less.'''

)
embedWhere = discord.Embed(
    title="Where is this bot hosted?",
    description='''`qr where` provides basic information on Q-Loggr's current host and region details.
    Steps
    1. Do qr where to access details.
    NOTE This is supposed to be a utility command and spamming the command will lead to API ratelimit for ipinfo. '''
)

# Getting all embeds in a list
helpList = [embedHelp, embedSave, embedFetch, embedPlayl, embedWhere]


# ----------------------------

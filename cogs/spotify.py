import discord
from discord import embeds
from discord.ext import commands
import aiohttp
import datetime
from PIL import Image, ImageDraw, ImageFont

from functools import partial

from io import BytesIO

from discord_components import (
    Button,
    ButtonStyle,
    Select,
    SelectOption,
    interaction,
)


class ImageCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=bot.loop)

    # getting the album cover
    async def get_image(self, url) -> BytesIO:
        async with self.session.get(url) as response:
            image_bytes = await response.read()

        return image_bytes

    # @commands.command(name='slect')
    # async def select(self, ctx):
    #     async def callback(interaction):
    #         await interaction.send(content="Yay")

    #     await ctx.send(
    #         "Select callbacks!",
    #         components=[
    #             self.bot.components_manager.add_callback(
    #                 Select(
    #                     options=[
    #                         SelectOption(label="a", value="a"),
    #                         SelectOption(label="b", value="b"),
    #                     ],
    #                 ),
    #                 callback,
    #             )
    #         ],
    #     )

    @staticmethod
    def imgen(delta1, delta2, title: str, artist: str, album: str, image_bytes: bytes) -> BytesIO:
        myFont2 = ImageFont.truetype("assets/code2000.ttf", 28)
        myFont1 = ImageFont.truetype("assets/code2000.ttf", 41)
        myFont3 = ImageFont.truetype("assets/Roboto-Regular.ttf", 19)

        m1 = divmod(delta1.seconds, 60)
        m2 = divmod(delta2.seconds, 60)
        # we must use BytesIO to load the image here as PIL expects a stream instead of
        # just raw bytes.
        with Image.open(BytesIO(image_bytes)) as im:
            with Image.open("assets/template.jpg") as background:
                img2 = im.resize((210, 210))
                background.paste(img2, (36, 36))
                draw = ImageDraw.Draw(background)

                # title
                draw.text((303, 36), "{}".format(
                    title[:23]), font=myFont1, fill="#befe00")

                #artist and album
                # draw.text((303, 99), "{}".format(str((artist))), font=myFont2, fill="#FFFFFF")
                draw.text((303, 99), fr"{artist[:33]}",
                          font=myFont2, fill="#FFFFFF")
                draw.text((303, 147), "{}".format(
                    album[:33]), font=myFont2, fill="#FFFFFF")

                # timestamps

                draw.text((303, 229), "{}:{}".format(str(m1[0]).zfill(
                    2), str(m1[1]).zfill(2)), font=myFont3, fill="#FFFFFF")
                draw.text((855, 229), "{}:{}".format(str(m2[0]).zfill(
                    2), str(m2[1]).zfill(2)), font=myFont3, fill="#FFFFFF")

                # total progress bar
                draw.rounded_rectangle(
                    (303, 211, 897, 221), radius=7, fill='#FFFFFF', outline=None, width=10
                )

                # current progress
                # some math
                xbar = int((delta1.seconds/delta2.seconds)*594)
                draw.rounded_rectangle(
                    (303, 211, 303+xbar, 221), radius=7, fill='#befe00', outline=None, width=10
                )
                # prepare the stream to save this image into
                final_buffer = BytesIO()

                # save into the stream, using png format.
                background.save(final_buffer, "png")

        # seek back to the start of the stream
        final_buffer.seek(0)

        return final_buffer

    @commands.command(name='spotify', aliases=['spot'])
    async def spotify(self, ctx, user: discord.Member = None):
        
        user = user or ctx.author
        if user.activities:
            for activity in user.activities:

                if isinstance(activity, discord.Spotify):
                    
                    delta1 = datetime.datetime.utcnow() - activity.start
                    delta2 = activity.end - activity.start
                    title = activity.title
                    artist = activity.artist
                    album = activity.album
                    url = activity.album_cover_url
                    songid = activity.track_id
                    spoturl = 'https://open.spotify.com/track/{}'.format(
                        songid)
                    image_bytes = await self.get_image(url)
                    
                    # create partial function so we don't have to stack the args in run_in_executor
                    fn = partial(self.imgen, delta1, delta2,
                                 title, artist, album, image_bytes)

                    final_buffer = await self.bot.loop.run_in_executor(None, fn)
                    file = discord.File(
                        filename="spotify.png", fp=final_buffer)

                    await ctx.reply(file=file, 
                        components=[Button(
                            style=ButtonStyle.URL, 
                            label="Play On Spotify", 
                            url=spoturl)])

            else:

                spotify = discord.Embed(
                    title="Uh Oh!",
                    description='''Looks like you aren't listening to **Spotify <:spotify:887426366818115585>** 
                        right now.Perhaps [give it a shot?](https://www.spotify.com/)''',
                    timestamp=datetime.datetime.now(),
                    colour=discord.Colour.gold(),
                ).set_footer(
                    text="Note that this command is a bit broken so just live with it."
                )

                await ctx.reply(embed=spotify)

        else:

            spotify = discord.Embed(
                title="Uh Oh!",
                description="Looks like you aren't listening to **Spotify <:spotify:887426366818115585>** right now. Perhaps [give it a shot?](https://www.spotify.com/)",
                timestamp=datetime.datetime.now(),
                colour=discord.Colour.gold(),
            ).set_footer(
                text="Note that this command is a bit broken so just live with it."
            )

            await ctx.reply(embed=spotify)


# setup function so this can be loaded as an extension
def setup(bot: commands.Bot):
    bot.add_cog(ImageCog(bot))

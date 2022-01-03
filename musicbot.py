import discord
from discord.ext import commands,tasks
import youtube_dl
from random import choice

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


client = commands.Bot(command_prefix='/')

status = ['Mixes Beat Like Jamba Juice','Escapism','Cactus Jack','Yo Chase B!']

@client.event
async def on_ready():
    change_status.start()
    print('Bot is Online')

#get ping
@client.command(name='ping',help='This command returns the latency')
async def ping(context):
    await context.send(f'Latency: {round(client.latency * 1000)} ms')

#show credits
# @client.command(name='credits',help='To all affliliated with this small project.')
# async def credits(context):
#     await context.send('Created by MrWhoseTheGoat')

@client.command(name='tune', help='This command plays music')
async def play(context, url):
    if not context.message.author.voice:
        await context.send("You are not connected to a voice channel, please try again.")
        return
      
    else:
        channel = context.message.author.voice.channel

    await channel.connect()

    server = context.message.guild
    voice_channel = server.voice_client

    async with context.typing():
        player = await YTDLSource.from_url(url, loop=client.loop)
        voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    await context.send('**Now playing:** {}'.format(player.title))

@client.command(name='stop',help='This command stops music.')
async def play(context):
    voice_client = context.message.guild.voice_client
    await voice_client.disconnect()
    
@tasks.loop(seconds=1000)
async def change_status():
    await client.change_presence(activity=discord.Game(choice(status)))



client.run('OTI3NjMyMjkwNjM1NDc3MDEz.YdNC5A.UWEdmjFMLy1uoHng7OdqKhEEPd0')

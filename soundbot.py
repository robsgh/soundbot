import discord
from discord.ext import commands
import asyncio

from os import listdir
from os.path import isfile, join
from os import environ

import ctypes.util

soundfiles = []

# load environment variables
SOUNDBOT_PREFIX = environ.get('SOUNDBOT_PREFIX', ';')
SOUNDBOT_TOKEN = environ.get('SOUNDBOT_TOKEN', None)
SOUNDBOT_ACTIVITY = environ.get('SOUNDBOT_ACTIVITY', '{}ls'.format(SOUNDBOT_PREFIX))

# create bot
bot = commands.Bot(SOUNDBOT_PREFIX)

@bot.event
async def on_ready():
    """ Called when the discord ready event is triggered """
    opus_lib_name = ctypes.util.find_library('opus')
    if not discord.opus.is_loaded():
        discord.opus.load_opus(opus_lib_name)
    if not os.path.exists('soundboard/'):
        print('ERROR: Please setup a soundboard directory. Read the README!')
        return

    # load sounds into memory
    await enumerate_sounds()
    # change activity message
    await bot.change_presence(activity=discord.Game(SOUNDBOT_ACTIVITY))

    print('Connected to discord as {0.user}!'.format(bot))

async def enumerate_sounds():
    """ Find all MP3 sound files in the soundboard/ directory """
    soundfiles.clear()

    # find all mp3 files in the soundboard directory
    for f in listdir('soundboard/'):
        if str(f).endswith('.mp3'):
            soundfiles.append(str(f).split('.')[0])

    # optional: sort the files alphabetically
    soundfiles.sort()

    print('Found {} sound files after load'.format(len(soundfiles)))

@bot.event
async def on_message(message):
    """ Process the messages sent to the bot """
    if message.author == bot.user:
        return
    elif message.content.startswith(SOUNDBOT_PREFIX) is False:
        return
    elif message.content in ['{}sounds'.format(SOUNDBOT_PREFIX), '{}list'.format(SOUNDBOT_PREFIX), '{}ls'.format(SOUNDBOT_PREFIX)]:
        await sounds(message)
    elif message.author.voice == None or message.author.voice.channel == None:
        await message.channel.send('You are not in a voice channel!')
        return

    # slice off the command prefix
    cmd = message.content[1:]
    for name in soundfiles:
        # if a file in the soundboard matches the command sent
        if name == cmd:
            print('Attempting to play {}'.format(cmd))
            vc = await message.author.voice.channel.connect()
            if not vc.is_connected():
                return
            audio_source = discord.FFmpegPCMAudio('soundboard/' + name + '.mp3')
            vc.play(audio_source)
            while vc.is_playing():
                await asyncio.sleep(1)
            vc.stop()
            await vc.disconnect()

async def sounds(message):
    """ List all sounds that are able to be played """
    msg = "```"
    counter = 1

    for name in soundfiles:
        msg += str(counter) + ". " + str(name) + "\n"
        counter += 1

    msg[:-1]
    msg += "\nPlay a sound with {}[sound]```".format(SOUNDBOT_PREFIX)

    await message.channel.send(msg)

if SOUNDBOT_TOKEN:
    bot.run(SOUNDBOT_TOKEN)
else:
    print('ERROR: Please specify a bot token (SOUNDBOT_TOKEN)!')


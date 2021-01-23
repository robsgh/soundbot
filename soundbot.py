import discord
from discord.ext import commands
import asyncio

import os

import ctypes.util

soundfiles = []

# load environment variables
SOUNDBOT_PREFIX = os.environ.get('SOUNDBOT_PREFIX', ';')
SOUNDBOT_TOKEN = os.environ.get('SOUNDBOT_TOKEN', None)
SOUNDBOT_ACTIVITY = os.environ.get('SOUNDBOT_ACTIVITY', '{}ls'.format(SOUNDBOT_PREFIX))

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

async def embed_list(title, description, column_header, list_to_embed, footer=None):
    print('Displaying rich embed with title of {}!'.format(title))

    embed = discord.Embed(title=title, description=description, color=0x8fc2c2)
    msg = ''
    for i in range(len(list_to_embed)):
        if len(msg) + len(list_to_embed[i]) >= 1000: # if max length for a field has been reached, add a new field
            embed.add_field(name=column_header, value=msg, inline=True)
            msg = ''

        msg += '`{}`'.format(list_to_embed[i])

        if len(msg) > 0 and i < len(list_to_embed) - 1:
            msg += ', '

    # msg could be blank here due to field additions
    if len(msg) > 0:
        embed.add_field(name=column_header, value=msg, inline=True)

    if footer:
        embed.set_footer(text=footer)

    return embed

async def sounds(message):
    """ List all sounds that are able to be played """

    sound_embed = await embed_list(
        title='Sound List', 
        description='All currently loaded sounds', 
        column_header=':loud_sound: Sound Names', 
        list_to_embed=soundfiles, 
        footer='Play a sound with "{}[sound name]"'.format(SOUNDBOT_PREFIX)
    )

    await message.channel.send(embed=sound_embed)


async def reload_list(message):
    """ Reload all soundfiles and display the changes """
    print('Reloading soundfiles now!')

    # Copy soundfiles before reloading to be able to calculate differences
    old_soundfiles = []
    for i in soundfiles:
        old_soundfiles.append(i)

    await enumerate_sounds()

    # create a list of sounds that are "new"
    new_sounds = [x for x in soundfiles if x not in old_soundfiles]

    new_embed = await embed_list(
        title='Newly-Discovered Sounds',
        description='SoundBot found {} new sounds!'.format(len(new_sounds)),
        column_header=':card_file_box: Sound Names',
        list_to_embed=new_sounds
    )

    await message.channel.send(embed=new_embed)
    
async def enumerate_sounds():
    """ Find all MP3 sound files in the soundboard/ directory """
    soundfiles.clear()

    # find all mp3 files in the soundboard directory
    for f in os.listdir('soundboard/'):
        soundname = os.path.splitext(str(f))[0]
        if os.path.isfile('soundboard/{}.mp3'.format(soundname)):
            soundfiles.append(soundname)

    # optional: sort the files alphabetically
    soundfiles.sort()

@bot.event
async def on_message(message):
    """ Process the messages sent to the bot """
    if message.author == bot.user or message.content.startswith(SOUNDBOT_PREFIX) is False:
        return
    elif message.content in ['{}sounds'.format(SOUNDBOT_PREFIX), '{}list'.format(SOUNDBOT_PREFIX), '{}ls'.format(SOUNDBOT_PREFIX)]:
        await sounds(message)
    elif message.content in ['{}reload'.format(SOUNDBOT_PREFIX), '{}rl'.format(SOUNDBOT_PREFIX)]:
        await reload_list(message)
    elif message.author.voice == None or message.author.voice.channel == None:
        await message.channel.send('You are not in a voice channel!')
    else:
        # slice off the command prefix
        cmd = message.content[len(SOUNDBOT_PREFIX):]
        for name in soundfiles:
            # if a file in the soundboard matches the command sent
            if name == cmd:
                print('Queueing sound: {}'.format(cmd))

                # attempt to reuse a vc if possible, otherwise join the vc if disconnected
                vc = None
                if len(bot.voice_clients) > 0:
                    # wait for all voice clients in the bot to stop playing
                    for bvc in bot.voice_clients:
                        while bvc.is_playing():
                            await asyncio.sleep(0.1)
                        # keep track of the vc
                        vc = bvc
                else:
                    # no previous vcs, join a new voice channel
                    vc = await message.author.voice.channel.connect()

                # create and play the sound through ffmpeg
                sound = discord.FFmpegPCMAudio('soundboard/{filename}.mp3'.format(filename=name))
                vc.play(sound)

                # stall while playing
                while vc.is_playing():
                    await asyncio.sleep(0.1)

                # stop playing after finishing the sound
                vc.stop()

                # wait a bit, and if no new sounds are playing disconnect from voice
                await asyncio.sleep(1)
                if len(bot.voice_clients) > 0 and not bot.voice_clients[0].is_playing():
                    await vc.disconnect()


if SOUNDBOT_TOKEN:
    bot.run(SOUNDBOT_TOKEN)
else:
    print('ERROR: Please specify a bot token (SOUNDBOT_TOKEN)!')


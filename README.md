# SoundBot
SoundBot is a containerized soundboard for Discord.

## How to use SoundBot
Populate a directory at ./soundboard/ with MP3 files.
Build and run the docker container with the following environment variables set:
* SOUNDBOT_TOKEN: The API token of the bot retrieved from the [Discord Developers Portal](https://discord.com/developers/applications)
* SOUNDBOT_PREFIX: The command prefix for the soundboard. The default is ';'.
* SOUNDBOT_ACTIVITY: The activity string for the bot user. This defaults to the help message.

## Notes
This containerized bot was designed for Kubernetes. 
While it will work fine in Docker alone (and with much less headaches!), the stateless nature of Discord
bots along with HA fares quite well for Kubernetes. If you have not played around with creating a 
Kubernetes cluster before, perhaps now is the time to start! 

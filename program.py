from player import MusicPlayer
from playlist import Playlist
from discord import Embed


class MainProgram(MusicPlayer, Playlist):
    def __init__(self):
        self.token = ''
        super(MainProgram, self).__init__()
        self.source_path = "./"

    def __set_method(self):
        async def __help(ctx, arg):
            c = self.bot.command_prefix
            cmd = desc = ""
            cmd += "***-- Music Player Command --***\n"
            desc += '--- \n'
            cmd += f"{c}join\n"; desc += "Make the bot join your current voice channel\n"
            cmd += f"{c}leave\n"; desc += "Make the bot leave your voice channel\n"
            cmd += f"{c}play\n"; desc += "Start playing from playlist\n"
            cmd += f"{c}pause\n"; desc += "Pause the current playing song\n"
            cmd += f"{c}resume\n"; desc += "Resume playing the current song\n"
            cmd += f"{c}skip\n"; desc += "Skip to the next song\n"
            cmd += "***-- Playlist Command --***\n"
            desc += '--- \n'
            cmd += f"{c}add *<index>*\n"; desc += "Add song from current directory into playlist\n"
            cmd += f"{c}search *[index]*\n"; desc += "Get a list of songs or move between directories\n"
            cmd += f"{c}playlist\n"; desc += "Show the current playlist\n"
            cmd += f"{c}shuffle\n"; desc += "Randomly shuffle the current playlist\n"
            cmd += f"{c}delete *<from> [to]*\n"; desc += "Delete songs from current playlist\n"
            cmd += f"{c}clear\n"; desc += "Clear the current playlist\n"
            e = Embed()
            e.title = "COMMAND LIST"
            e.add_field(name='COMMAND', value=cmd)
            e.add_field(name='DESCRIPTION', value=desc)
            await self.send_embed(ctx, e)
        self.add_func('help', __help)

    # Public method

    def start(self):
        MusicPlayer.start(self)
        Playlist.start(self)
        self.__set_method()
        self.start_bot()

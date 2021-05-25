from bot import BotModule
import discord, asyncio

"""
Song syntax:
{
    "name": "song name",
    "path": "song path",
    "t_path": "temp path",
    "type": "file type"
}
"""


class MusicPlayer(BotModule):
    def __init__(self):
        super(MusicPlayer, self).__init__()
        self.queue = []
        self.playing = None

    async def __user_in_voice(self, ctx):
        user_voice = ctx.author.voice
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if user_voice is None:
            await self.send_back(ctx, 'User has not joined any voice yet')
            return False
        elif voice_client is None:
            await self.send_back(ctx, 'Bot has not joined any voice yet')
            return False
        elif voice_client.channel != user_voice.channel:
            await self.send_back(ctx, 'User is not in the same voice channel with bot')
            return False
        return True

    def __play_next(self, ctx):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client is not None:
            if not voice_client.is_playing():
                if len(self.queue) > 0:
                    song = self.queue.pop(0)
                    self.playing = song
                    asyncio.run_coroutine_threadsafe(self.send_back(ctx, f'Playing: {song["name"]}'), self.bot.loop)
                    voice_client.play(discord.FFmpegPCMAudio(song["path"]), after=lambda e: self.__play_next(ctx))
                else:
                    self.playing = None
                    asyncio.run_coroutine_threadsafe(self.send_back(ctx, 'Queue is empty'), self.bot.loop)

    # Command

    async def __join(self, ctx, arg):
        user_voice = ctx.author.voice
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if user_voice is None:
            await self.send_back(ctx, f'User has not joined any voice yet')
        else:
            if voice_client is None:
                await self.send_back(ctx, f'Join to voice: {user_voice.channel}')
                await user_voice.channel.connect()
            else:
                await self.send_back(ctx, f'Jump to voice: {user_voice.channel}')
                await voice_client.move_to(user_voice.channel)

    async def __leave(self, ctx, arg):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client is None:
            await self.send_back(ctx, 'No voice available. Can not leave')
        else:
            self.queue.clear()
            self.playing = None
            if voice_client.is_connected():
                if voice_client.is_playing():
                    voice_client.stop()
                await voice_client.disconnect()
            else:
                await self.send_back(ctx, 'Bot has not joined any voice yet')

    async def __play(self, ctx, arg):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client.is_paused():
            voice_client.resume()
        elif voice_client.is_playing():
            await self.send_back(ctx, 'Bot is already playing')
        else:
            self.__play_next(ctx)

    async def __pause(self, ctx, arg):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client.is_playing():
            voice_client.pause()

    async def __resume(self, ctx, arg):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client.is_paused():
            voice_client.resume()

    async def __skip(self, ctx, arg):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client.is_playing():
            voice_client.stop()

    # Public method

    def start(self):
        async def join(ctx, arg):
            await self.__join(ctx, arg)
        self.add_func('join', join)

        async def leave(ctx, arg):
            await self.__leave(ctx, arg)
        self.add_func('leave', leave)

        async def play(ctx, arg):
            if await self.__user_in_voice(ctx):
                await self.__play(ctx, arg)
        self.add_func('play', play)

        async def pause(ctx, arg):
            if await self.__user_in_voice(ctx):
                await self.__pause(ctx, arg)
        self.add_func('pause', pause)

        async def resume(ctx, arg):
            if await self.__user_in_voice(ctx):
                await self.__resume(ctx, arg)
        self.add_func('resume', resume)

        async def skip(ctx, arg):
            if await self.__user_in_voice(ctx):
                await self.__skip(ctx, arg)
        self.add_func('skip', skip)

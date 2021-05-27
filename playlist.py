from bot import BotModule
import os, random


class Playlist(BotModule):
    def __init__(self):
        super(Playlist, self).__init__()
        self.queue = []
        self.source_path = ''
        self.current_path = ""
        self.song_list = []
        self.playing = None
        self.formats = ['.mp3', '.mp4', '.wav', '.flac', '.wma', '.ogg', '.m4a', '.webm']

    async def __get_song(self, ctx, index, song_list):
        if len(song_list) == 0:
            await self.send_back(ctx, 'No song available !')
            return None
        else:
            try:
                file_index = int(index)
                if file_index < 1 or file_index > len(song_list):
                    await self.send_back(ctx, 'Value out of range !')
                    return None
                else:
                    return song_list[file_index - 1]
            except ValueError:
                await self.send_back(ctx, 'Value error !')
                return None

    def __retrieve_list(self, t_path):
        song_list = []
        parent_path = os.path.join(self.source_path, t_path)
        for name in os.listdir(parent_path):
            path = os.path.join(parent_path, name)
            if os.path.isfile(path):
                _type = "file"
                if os.path.splitext(name)[1].lower() not in self.formats:
                    continue
            else:
                _type = "folder"
            temp_path = os.path.join(t_path, name)
            song_list.append({
                "name": name,
                "path": path,
                "t_path": temp_path,
                "type": _type
            })
        return song_list

    # Command

    def change_source(self, source):
        self.song_list.clear()
        self.source_path = source
        self.current_path = ""

    async def __search(self, ctx, arg):
        if arg == "":
            pass
        elif arg == "/":
            self.current_path = ""
        elif arg == "0":
            if self.current_path != "":
                self.current_path, _ = os.path.split(self.current_path)
        else:
            song = await self.__get_song(ctx, arg, self.song_list)
            if song is None:
                return
            else:
                if os.path.isdir(song['path']):
                    self.current_path = song["t_path"]
                else:
                    await self.send_back(ctx, 'Can not list file path')
                    return
        self.song_list = self.__retrieve_list(self.current_path).copy()
        folder_count = file_count = word_count = 0
        for song in self.song_list:
            if song['type'] == "folder":
                folder_count += 1
            else:
                file_count += 1
        msg = f"        **FILE LIST FROM /{self.current_path}**\n\n"
        msg += ("0  -  ...\n" if self.current_path != "" else "")
        for count in range(len(self.song_list)):
            song = self.song_list[count]
            new_msg = f"{count + 1}  -  {song['name']}" + ("/" if song['type'] == "folder" else "") + '\n'
            if word_count + len(new_msg) > 1800:
                msg += '..................\n'
                break
            else:
                msg += new_msg
                word_count += len(new_msg)
        msg += f"\n*{folder_count} folders and {file_count} songs found*"
        await self.send_back(ctx, msg)

    async def __add(self, ctx, arg):
        new_queue = []
        song = await self.__get_song(ctx, arg, self.song_list)
        if song is not None:
            if song["type"] == "file":
                new_queue.append(song)
            else:
                folder_list = [song]
                while len(folder_list) > 0:
                    c_song = folder_list.pop(0)
                    new_list = self.__retrieve_list(c_song['t_path'])
                    for t_song in new_list:
                        if t_song["type"] == "folder":
                            folder_list.append(t_song)
                        else:
                            new_queue.append(t_song)
        for song in new_queue:
            self.queue.append(song)
        await self.send_back(ctx, f'{len(new_queue)} songs added')

    async def __playlist(self, ctx, arg):
        msg = f"Playing: {'None' if self.playing is None else self.playing['name']}\n\n"
        if len(self.queue) == 0:
            msg += "*(empty)*"
        else:
            word_count = 0
            for count in range(len(self.queue)):
                song = self.queue[count]
                new_msg = f"{count + 1}  -  {song['name']}\n"
                if word_count + len(new_msg) > 1800:
                    msg += '..................\n'
                    break
                else:
                    msg += new_msg
                    word_count += len(new_msg)
            msg += f'\n*{len(self.queue)} songs in playlist*'
        await self.send_back(ctx, msg)

    async def __shuffle(self, ctx, arg):
        random.shuffle(self.queue)
        await self.send_back(ctx, 'Shuffle done !')

    async def __delete(self, ctx, arg):
        if len(arg) == 1:
            if await self.__get_song(ctx, arg[0], self.queue) is not None:
                self.queue.pop(int(arg[0]) - 1)
                await self.send_back(ctx, '1 song deleted')
        elif len(arg) == 2:
            if (await self.__get_song(ctx, arg[0], self.queue) is not None) \
                    and (await self.__get_song(ctx, arg[1], self.queue) is not None):
                start = int(arg[0])
                end = int(arg[1])
                if start > end:
                    await self.send_back(ctx, 'Range error !')
                else:
                    del self.queue[start - 1:end]
                    await self.send_back(ctx, f'{end - start + 1} songs deleted')
        else:
            await self.send_back(ctx, 'Argument error !')

    async def __clear(self, ctx, arg):
        self.queue.clear()
        await self.react_yes(ctx)

    async def __sort(self, ctx, arg):
        self.queue.sort(key=lambda d: d['name'])
        await self.react_yes(ctx)

    async def __next(self, ctx, arg):
        if len(arg) < 1:
            await self.send_back(ctx, 'Song index needed')
        else:
            song = await self.__get_song(ctx, arg[0], self.queue)
            if song is not None:
                self.queue.insert(0, self.queue.pop(self.queue.index(song)))
                await self.react_yes(ctx)

    # Public method

    def start(self):
        async def add(ctx, arg):
            n_arg = "" if len(arg) == 0 else arg[0]
            await self.__add(ctx, n_arg)
        self.add_func('add', add)

        async def search(ctx, arg):
            n_arg = "" if len(arg) == 0 else arg[0]
            await self.__search(ctx, n_arg)
        self.add_func('search', search)

        async def playlist(ctx, arg):
            await self.__playlist(ctx, arg)
        self.add_func('playlist', playlist)

        async def shuffle(ctx, arg):
            await self.__shuffle(ctx, arg)
        self.add_func('shuffle', shuffle)

        async def delete(ctx, arg):
            await self.__delete(ctx, arg)
        self.add_func('delete', delete)

        async def clear(ctx, arg):
            await self.__clear(ctx, arg)
        self.add_func('clear', clear)

        async def sort(ctx, arg):
            await self.__sort(ctx, arg)
        self.add_func('sort', sort)

        async def _next(ctx, arg):
            await self.__next(ctx, arg)
        self.add_func('next', _next)

import googleapiclient.discovery
import googleapiclient.errors

import pafy

import discord
import random
import os

from urllib.parse import urlparse, parse_qs
from discord.ext import commands
from .common_functions import MultiPagePrinter

class MusicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = []
        self.current_song = 0
        self.is_looped = False
        self.is_playing = False
        self.client = None

        self.ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -dn -sn -ignore_unknown -tune zerolatency'}

        self.yt_api = os.environ['YOUTUBE_API']
        self.playlist_id = os.environ['PLAYLIST_ID']
        self.api_service_name = 'youtube'
        self.api_version = 'v3'

        self.setup()

    def setup(self):
        print('Music commands loaded')

    def next_song(self, error=None):
        if error:
            self.current_song = 0
            self.client = None
            self.is_playing = False
            return
            
        self.current_song += 1
        
        if not self.is_looped and self.current_song >= len(self.song_queue):
            self.current_song = 0
            self.is_playing = False
            self.client.stop()
            return

        self.current_song %= len(self.song_queue)
        if self.client:
            self.client.pause()

        self.play_song(self.client, self.song_queue[self.current_song]['url'])

    def play_song(self, voice_client, link):
        url = pafy.new(link).getbestaudio().url
        if self.is_playing:
            voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url, **self.ffmpeg_options)), after=lambda e: self.next_song())

    def title_from_yt_url(self, url):
        if url.startswith(('youtu', 'www')):
            url = 'http://' + url
        query = urlparse(url)

        video_id = ''
        if 'youtube' in query.hostname:
            if query.path == '/watch':
                video_id = parse_qs(query.query)['v'][0]
            elif query.path.startswith(('/embed/', '/v/')):
                video_id = query.path.split('/')[2]
        elif 'youtu.be' in query.hostname:
            video_id = query.path[1:]
        else:
            raise ValueError

        youtube = googleapiclient.discovery.build(self.api_service_name,
                                                self.api_version,
                                                developerKey=self.yt_api)
        request = youtube.videos().list(part='snippet',
                                        id=video_id)
        response = request.execute()
        return response['items'][0]['snippet']['title']

    def get_quick_playlist(self):
        youtube = googleapiclient.discovery.build(self.api_service_name,
                                                self.api_version,
                                                developerKey=self.yt_api)
        page_token = ''

        while True:
            request = youtube.playlistItems().list(part='snippet',
                                                playlistId=self.playlist_id,
                                                pageToken=page_token)
            response = request.execute()
            for item in response['items']:
                video = {
                    'title' : item['snippet']['title'],
                    'url' : f'https://www.youtube.com/watch?v={item["snippet"]["resourceId"]["videoId"]}'
                }
                self.song_queue.append(video)

            if 'nextPageToken' in response:
                page_token = response['nextPageToken']
            else:
                break

    async def list_queue(self, ctx):
        if not len(self.song_queue) > 0:
            await ctx.send(':pizza: Queue is empty')
            return
        titles = []
        for song in self.song_queue:
            titles.append(f'[{song["title"]}]({song["url"]})')
        printer = MultiPagePrinter(self.bot, ctx, titles, 'Current Queue', 10)
        await printer.print()

    async def add_to_queue(self, ctx, link):
        if 'youtube.com/watch?v=' in link or 'youtu.be/watch?v=' in link:
            title = self.title_from_yt_url(link)
            song = {
                'title' : title,
                'url' : link
            }
            self.song_queue.append(song)
            await self.print_embed(ctx, 'Add to Queue', f'Added "{title}" to the queue')

    async def print_embed(self, ctx, title, desc):
        embed = discord.Embed(title=f':pizza: {title}', description=f'{desc}', colour=discord.Colour.dark_gold())
        await ctx.send(embed=embed)

    @commands.command(aliases=['join'])
    async def _join_voice_channel(self, ctx):
        if ctx.author.voice is None:
            await ctx.send(f':pizza: <@{ctx.author.id}>, you are not in a voice channel')
            return
        elif ctx.voice_client is not None and ctx.voice_client.is_connected():
            await ctx.voice_client.disconnect()
        else:
            channel = ctx.author.voice.channel
        await channel.connect()
        self.client = ctx.voice_client
        await ctx.channel.send(':pizza: Hello')

    @commands.command(aliases=['leave'])
    async def _leave_voice_channel(self, ctx):
        if self.is_playing:
            self.is_playing = False
        voice_client = ctx.voice_client
        if voice_client is not None and voice_client.is_connected():
            self.client = None
            await voice_client.disconnect()
            await ctx.send(':pizza: Bye')
        else:
            await ctx.send(':pizza: I\'m not in a voice channel')

    @commands.command(aliases=['quickplay', 'qp'])   
    async def _quickplay(self, ctx):
        if self.is_playing:
            await ctx.send(':pizza: Already playing music, aborting')
            return

        if not ctx.voice_client:
            await self._join_voice_channel(ctx)

        self.get_quick_playlist()
        await self._shuffle(ctx)

        self.current_song = 0
        self.is_playing = True

        if ctx.voice_client and not self.client:
            self.client = ctx.voice_client

        await ctx.send(':pizza: Playing Quick Playlist')
        self.play_song(ctx.voice_client, self.song_queue[self.current_song]['url'])

    @commands.command(aliases=['play'])
    async def _play(self, ctx):
        if not len(self.song_queue) > 0:
            await ctx.send(':pizza: Queue is empty')
            return

        if not ctx.voice_client:
            await self._join_voice_channel(ctx)

        self.current_song = 0
        self.is_playing = True

        if ctx.voice_client:
            self.client = ctx.voice_client
            
        self.play_song(ctx.voice_client, self.song_queue[self.current_song]['url'])
        await self.print_embed(ctx, 'Play', f'Playing "{self.song_queue[self.current_song]["title"]}"')
        

    @commands.command(aliases=['pause'])
    async def _pause(self, ctx):
        if not ctx.voice_client:
            return
        if not ctx.voice_client.is_paused():
            ctx.voice_client.pause()
            await ctx.send(':pizza: Paused')

    @commands.command(aliases=['resume'])
    async def _resume(self, ctx):
        if not ctx.voice_client:
            return
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send(':pizza: Resumed')

    @commands.command(aliases=['stop'])
    async def _stop(self, ctx):
        self.song_queue.clear()
        self.client.stop()
        self.is_playing = False
        self.client = None
        if not ctx.voice_client:
            return
        await ctx.send(':pizza: Stopped')

    @commands.command(aliases=['next'])
    async def _next(self, ctx):
        if not ctx.voice_client or not self.is_playing:
            return
        
        self.next_song()
        await self.print_embed(ctx, 'Skip', f'Playing "{self.song_queue[self.current_song]["title"]}"')

    @commands.command(aliases=['clear'])
    async def _clear(self, ctx):
        self.song_queue.clear()
        await ctx.send(':pizza: Queue cleared')
        self.client.stop()

    @commands.command(aliases=['shuffle'])
    async def _shuffle(self, ctx):
        random.shuffle(self.song_queue)
        self.current_song = len(self.song_queue) - 1 if len(self.song_queue) > 0 else 0
        await ctx.send(':pizza: Queue shuffled')

    @commands.command(aliases=['loop'])
    async def _loop(self, ctx):
        self.is_looped = not self.is_looped
        loop_msg = 'on' if self.is_looped else 'off'
        await ctx.send(f':pizza: Queue loop is now {loop_msg}')

    @commands.command(aliases=['queue'])
    async def _queue(self, ctx, *args):
        if len(args) == 1:
            if args[0] == 'list':
                await self.list_queue(ctx)
                return
            if args[0] == 'current':
                if not self.is_playing:
                    await ctx.send(':pizza: Currently not playing')
                    return

                if not len(self.song_queue) > 0:
                    await ctx.send(':pizza: Queue is empty')
                    return
                paused_msg =  ' (paused)' if ctx.voice_client.is_paused() else ''
                song_title = self.song_queue[self.current_song]['title']
                song_number = self.current_song
                await self.print_embed(ctx, 'Current', f'Playing {paused_msg} #{song_number + 1}"{song_title}"')
                return
        
        if len(args) == 2:
            if args[0] == 'add':
                await self.add_to_queue(ctx, args[1])
                return
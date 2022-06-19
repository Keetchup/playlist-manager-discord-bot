import googleapiclient.discovery
import googleapiclient.errors

import pickle
import google_auth_oauthlib.flow

import os
from discord.ext import commands

from .common_functions import MultiPagePrinter

class PlaylistCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.yt_api = os.environ['YOUTUBE_API']
        self.playlist_id = os.environ['PLAYLIST_ID']
        self.api_service_name = 'youtube'
        self.api_version = 'v3'

        self.scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
        self.client_secrets_file = "./config/client_secret_file.json"

        self.setup()

    def setup(self):
        print('Playlist commands loaded')

    def get_oauthorization(self):
        if os.path.exists('CREDENTIALS_PICKLE_FILE'):
            with open('CREDENTIALS_PICKLE_FILE', 'rb') as f:
                credentials = pickle.load(f)
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                self.client_secrets_file, self.scopes)
            credentials = flow.run_console()
            with open('CREDENTIALS_PICKLE_FILE', 'wb') as f:
                pickle.dump(credentials, f)
        return googleapiclient.discovery.build(self.api_service_name,
                                            self.api_version,
                                            credentials=credentials)

    async def list_playlist(self, ctx):
        youtube = googleapiclient.discovery.build(self.api_service_name,
                                                self.api_version,
                                                developerKey=self.yt_api)
        page_token = ''
        videos = []

        while True:
            request = youtube.playlistItems().list(part='snippet',
                                                playlistId=self.playlist_id,
                                                pageToken=page_token)
            response = request.execute()
            for item in response['items']:
                videos.append(item['snippet']['title'])

            if 'nextPageToken' in response:
                page_token = response['nextPageToken']
            else:
                break
        printer = MultiPagePrinter(self.bot, ctx, videos, 'Quick Playlist', 10)
        await printer.print()
        

    async def add_to_playlist(self, ctx, link):
        youtube = self.get_oauthorization()
        
        request = youtube.playlistItems().insert(part='snippet',
                                                body={
                                                    'snippet': {
                                                        'playlistId':
                                                        self.playlist_id,
                                                        'resourceId': {
                                                            'kind':
                                                            'youtube#video',
                                                            'videoId':
                                                            link
                                                        }
                                                    }
                                                })
        response = request.execute()
        title = response['snippet']['title']
        await ctx.send(f':pizza: Added "{title}" to the playlist')

    @commands.command(aliases=['playlist', 'playlistmngr'])
    async def _playlist(self, ctx, *args):
        if len(args) == 1:
            if args[0] == 'list':
                await self.list_playlist(ctx)
                return

        if len(args) == 2:
            if args[0] == 'add':
                link_prefix = 'https://www.youtube.com/watch?v='
                if args[1].startswith(link_prefix):
                    await self.add_to_playlist(ctx, args[1].replace(link_prefix, ''))
                    return
                else:
                    await ctx.send(':pizza: Rejected. Not an Youtube link')
                    return
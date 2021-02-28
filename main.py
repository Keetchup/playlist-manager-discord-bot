import discord

import googleapiclient.discovery
import googleapiclient.errors

import pickle
import google.oauth2.credentials
import google_auth_oauthlib.flow

import os

from keep_alive import keep_alive

discord_client = discord.Client()

yt_api = os.getenv('YOUTUBE_API')
playlist_id = os.getenv('PLAYLIST_ID')
api_service_name = 'youtube'
api_version = 'v3'

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
client_secrets_file = "client_secret_file.json"

list_command = '-playlistmngr list'
add_command = '-playlistmngr add https://www.youtube.com/watch?v='

@discord_client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(discord_client))

@discord_client.event
async def on_message(message):
  if message.author == discord_client.user:
    return
  if message.content.startswith(list_command):
    youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey = yt_api)


    page_token = ''
    videos = []

    while True:
      request = youtube.playlistItems().list(
        part = 'snippet',
        playlistId = playlist_id,
        pageToken = page_token
      )
      response = request.execute()
      for item in response['items']:
        videos.append(item['snippet']['title'])

      if 'nextPageToken' in response:
        page_token = response['nextPageToken']
      else:
        break

    result_string = '```'
    iterator = 1
    for video in videos:
      result_string = result_string + str(iterator) + ') ' + video
      if video == videos[-1]:
        result_string = result_string + '```'
        await message.channel.send(result_string)
      else:
        if iterator % 10 == 0:
          result_string = result_string + '```'
          await message.channel.send(result_string)
          result_string = '```'
        else:
          result_string = result_string + '\n'
      iterator += 1

  if message.content.startswith(add_command):
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    client_secrets_file, scopes)

    youtube = get_oauthorization()


    command = message.content
    video_id = command.replace(add_command, '')
    request = youtube.playlistItems().insert(
      part = 'snippet',
      body = {
        'snippet': {
          'playlistId': playlist_id,
          'resourceId': {
            'kind': 'youtube#video',
            'videoId': video_id
          }
        }
      }
    )
    response = request.execute()
    title = response['snippet']['title']
    await message.channel.send('```Added ' + title + '```')

def get_oauthorization():
  if os.path.exists('CREDENTIALS_PICKLE_FILE'):
    with open('CREDENTIALS_PICKLE_FILE', 'rb') as f:
        credentials = pickle.load(f)
  else:
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
    credentials = flow.run_console()
    with open('CREDENTIALS_PICKLE_FILE', 'wb') as f:
      pickle.dump(credentials, f)
  return googleapiclient.discovery.build(
    api_service_name, api_version, credentials=credentials)

discord_client.run(os.getenv('TOKEN'))



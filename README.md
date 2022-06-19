# discord-yt-playlist-manager

## How to run

### Building docker image

`docker build -t [image-name] .`

### Running built docker image

`docker run -d -e TOKEN=[discord-token] -e YOUTUBE_API=[youtube-api-token] -e PLAYLIST_ID=[yt-playlist-id] --name [container-name] [image-name]`

## It does not work?

Youtube removed dislike from YoutubeAPI and this project uses pafy as a way to fetch information. This library has not been updated since late 2019. There are pull requests with a fix however it has not been merged yet. You might want to used forked pafy repositories.

## Commands

`/commands`
Lists all commands

### Music

`/join`
Bot connects to voice channel you are currently in

`/leave`

`/quickplay` | `/qp`
Joins voice channel adds videos from playlist defined by PLAYLIST_ID environment variable and starts playing

`/queue list`

`/queue add [yt-url]`

`/queue current`

`/play`

`/stop`

`/pause`

`/resume`

`/next`

`/loop`
Toggles loop setting

`/clear`
Empties song queue

### Playlist

`/playlist list`
Lists all video within a playlist

`/playlist add [yt-url]`
Adds a video to a playlist

### Other

These were made just for fun

`/delka`

`/sirka`

`/lockdown`
Copypasta

`/coin`
Coinflip

`/rng [x] [y]`
Pseudo randomly selects number between x and y

Docker script, which monitors specified source directories for new Movie/Show additions and creates symlinks in the specified destination folders.

#### Use case
light-weight Real-debrid integration with *arr stack. 

Pros:
* Quick symlink creation
* Manually choose your preferred media types and sizes
* Ability to easily import whole seasons
* Organized library
* Accurate Plex Agent content matching

Be sure to stop container if used in conjuction with rdt-client or similar, as it will duplicate entries and cause mess.

#### Usage

Specify source as RD rclone mount (or zurg) and destination as Sonarr/Radarr library dir (dir which Plex/Jellyfin/Emby is monitoring). Then add content via RD (https://debridmediamanager.com/ or whatever you choose) and get your content show up in *arr. 
Script will monitor specified dirs in 10s intervals and match the names to **existing** folders in destination dirs. Make sure to add content in *arr first, so it would create appropriate dirs (or do it manually).

**docker-compose.yml**
```  
version: '3.9'
services:
  auto-symlink:
    container_name: auto-symlink
    image: aidotas/auto_symlink
    environment:
      - PUID=1000 # specify your PUID to avoid permission issues
      - PGID=1000 # specify your PGID to avoid permission issues
      - TZ=Europe/London
      - SOURCE_DIRECTORY_SHOWS=/torrents/shows # RD rclone mount for shows
      - SOURCE_DIRECTORY_MOVIES=/torrents/movies # RD rclone mount for movies
      - DESTINATION_DIRECTORY_SHOWS=/data/tv # *arr/Plex library dir for shows
      - DESTINATION_DIRECTORY_MOVIES=/data/movies # *arr/Plex library dir for movies
      - DESTINATION_DIRECTORY_UHD_SHOWS=/data/tv-uhd # *arr/Plex library dir for 4k shows
      - DESTINATION_DIRECTORY_UHD_MOVIES=/data/movies-uhd # *arr/Plex library dir for 4k movies
      - UHD_LIBRARY=True # True if you have a separate library/dir for 4K content
    volumes:
      - realdebrid:/torrents # be sure to mount your rclone RD volume
      - /data:/data
    tty: true
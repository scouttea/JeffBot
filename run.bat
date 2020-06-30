docker build --tag discordbot .
docker run --mount source=botvolume,target=/local -it discordbot

pause
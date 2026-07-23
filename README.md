# logs-analyzer
Allows to diagnose the most common errors from Minecraft logs. Use the from_url variable to toggle between fetching from a local file and fetching from a discord-paste.curseforge.com or paste.ntms.link URL. Can analyze latest.log and launcher_log.txt files.

## Detection features :
- incorrect/missing dependencies
- missing/unsupported dependency
- incompatible Corgilib version
- corrupted config files
- red herring errors
- duplicate mods
- conflict between Rubidium and Embeddium
- outdated drivers
- Mac display issues
- MixinExtras conflict
- MixinExtras incorrect inclusion
- Xenon/Embeddium/Rubidium conflict
- maximum ID range (for 1.12)
- Unsupported mods in profile
- Minecraft launching with wrong videocard
- NBT too long
- Distant Horizon and Oculus/Iris not compatible
- important tag failing to load
- mod accessing a single threaded resource from multiple threads
- malformed options.txt
- client mod on server

"""
@author: dulph
@version: 1.0.0
"""
import regex
from_url = input("From URL ? (y/n)") == "y" #Default mode is False, requiring only regex module

class FetchingError(Exception):
	pass

def format_output(output, groups):
	for i in range(len(groups)):
		if groups[i] != None:
			output = output.replace("%GROUP" + str(i + 1) + "%", groups[i])
		else:
			output = output.replace("%GROUP" + str(i + 1) + "%", "")
	return output

def search_content(re, content, output):
	matches = regex.search(re, content)
	if matches != None:
		groups = matches.groups()
		return format_output(output, groups) + "\n\n"
	return ""

if from_url:
	from selenium import webdriver
	import time
	from bs4 import BeautifulSoup

	options = webdriver.FirefoxOptions()
	options.add_argument("--headless")

	url = input("Url ? ")
	url = url.split("#")[0]
	if not url.endswith("&raw=true"):
		url += "&raw=true"
	browser = webdriver.Firefox(options=options)
	browser.get(url)
	time.sleep(0.5)
	html = browser.page_source
	soup = BeautifulSoup(html, 'lxml')
	frame = soup.find(id="rawframe")
	waiting_time = 0.5
	attempts_count = 0
	while frame == None and attempts_count < 10:
		waiting_time += 0.25
		browser.get(url)
		time.sleep(waiting_time)
		html = browser.page_source
		soup = BeautifulSoup(html, 'lxml')
		frame = soup.find(id="rawframe")
		attempts_count += 1
	
	if frame.pre == "<pre><p>File not available.</p><p>Paste files are kept for up to 7 days with your privacy in mind.</p></pre>":
		raise FetchingError("ERROR: The file doesn't exist anymore")
	if frame == None:
		raise FetchingError("ERROR: Fetching failed. Please check the following:\n- The URL is a discord-paste.curseforge.com paste\n- The paste at this URL still exists")
	content = frame.pre.string
else:
	file = input("File path ? ")
	opened = open(file)
	content = opened.read()


#Problem 1 (incorrect/missing dependency)
re = r"Mod (?:§\w)*([a-z0-9_-]{2,64})(?:§\w)* requires (?:§\w)*([a-z0-9_-]{2,64})(?:§\w)* (?:§\w)*(between )?(?:§\w)*([0-9.]+) (and )?((?:[0-9.]+(?: \(inclusive\))?)|(?:or above))(, and below )?(?:§\w)*([0-9.]+)?(?:§\w)*\n\s*(?:§\w)*Currently, (?:§\w)*[a-z0-9_-]{2,64}(?:§\w)* is (?:§\w)*((?:not installed)|[0-9.]+)"
output = """The mod `%GROUP1%` requires the mod `%GROUP2%` installed.
It needs %GROUP3%version %GROUP4% %GROUP5%%GROUP6%%GROUP7%%GROUP8%, but it is currently %GROUP9%!"""
print(search_content(re, content, output), end="")

#Problem 1 version 2 (missing/unsupported dependency)
re = r"(Missing or unsupported|Unsupported installed) (mandatory|optional) dependencies:\s+Mod ID: '([a-zA-Z0-9_-]+)', Requested by: '([a-zA-Z0-9_-]+)', Expected range: '\[([0-9\.a-zA-Z-]+,[0-9\.a-zA-Z-]*)\)', Actual version: '([0-9\.a-zA-Z\[\]-]+)'"
output = """The mod `%GROUP4%` requires the mod `%GROUP3%` installed.
It needs version %GROUP5%, but is currently %GROUP6%!"""
print(search_content(re, content, output), end="")

#Problem 2 (Corgilib)
re = r"corgilib-Forge-4.0.2.0.jar|java\.lang\.module\.ResolutionException: Module [a-z_\-.0-9]+ reads more than one module named com\.electronwill\.nightconfig"
output = """It has been detected that the log has an incompatible mod version of `CorgiLib`. This contains a version of nightconfig inside `core-3.6.7.jar`, which is already in Forge by default.

> Possible solution:
>  Downgrade `CorgiLib` to version `4.0.1.3`.
>   Either use the app or this [file link](https://www.curseforge.com/minecraft/mc-mods/corgilib/files/5436749)."""
print(search_content(re, content, output), end="")

#Problem 3 diagnosis 2 (corrupted config files -> detailed)
re = r"net\.minecraftforge\.fml\.config\.ConfigFileTypeHandler\$ConfigLoadingException: Failed loading config file ([a-zA-Z0-9_\.-]+) of type ([A-Z]+) for modid ([a-zA-Z_-]+)|Failed to load ([a-zA-Z0-9]+) config from ⋖APPDIR⋗\\Instances\\([a-zA-Z0-9 ._-]+)\\config\\([a-zA-Z0-9._-]+)"
output = """The configuration file `%GROUP1%%GROUP6%` is corrupted. This often happens due to extreme crashes such as JVM errors or bluescreens.

The file must be removed to fix the profile.
**Options to remove corrupted config files:**
- Find the file mentioned above (probably inside the profiles `config` folder, however `server` type configs are sometimes in `saves/worldname/serverconfig` instead) and delete it.
- Get the community created [helper script from this Curseforge community github site](https://github.com/CurseForgeCommunity/Script-Tools) and run it to scan for, and remove corrupted config files.
    - Place a copy of the script file in the profile folder you would like to repair. To find the profile folder - Enter the profile screen in the Curseforge app, go to **options** <:zCFmenu:1319318631770751086> and then select **open folder**
    - Run the file which you have copied to the profile folder, wait for it to finish scanning - and confirm if you would like to remove what it found."""
print(search_content(re, content, output), end="")

#Problem 4 (cascading errors)
re = "Cowardly refusing to send event"
output = "Look for the error before `Cowardly refusing to send event`"
print(search_content(re, content, output), end="")

#Problem 5 (duplicate mods)
re = r"Found duplicate mods:\n\s*Mod ID: '([a-z0-9_-]{2,64})' from mod files: ((?:.+\.jar,? ?)+)"
output = """You have multiple copies of the mod `%GROUP1%`!
This is usually caused by having the real mod and another mod pretending to be that mod.

You need to remove all but one of following mods to resolve this issue:
`%GROUP2%`"""
print(search_content(re, content, output), end="")

#Problem 6 (conflict between Rubidium and Embeddium)
re = r"Mod ID: 'rubidium' from mod files: rubidium-(.+?)\.jar, embeddium"
output = """It has been detected that the two mods named `Rubidium` and `Embeddium` are both present in the uploaded log file.

This causes a conflict during load. To resolve it, one of the two mods must be removed.

> Possible solution:
>  Since `Rubidium` is older and is no longer updated, remove that mod."""
print(search_content(re, content, output), end="")

#Problem 7 (outdated drivers)
re = r"((Trying GL version \d\.\d|Backend library: LWJGL version \d\.\d\.\d build \d|You can safely ignore this message if the game starts up successfully.)$|#\s*Problematic\s*frame:\s*#\s*C\s*\[atio6axx\.dll\+0x)"
output = "Possible outdated drivers found. Run command !mc-amd and follow the instructions to fix"
print(search_content(re, content, output), end="")

#Problem 8 (mac display issues)
re = r"GLFW error before init: \[.*?\]Cocoa: Failed to find service port for display"
output = "Possible Mac display issues. Run command !mc-mac and follow the instructions to fix"
print(search_content(re, content, output), end="")

#Problem 9.1 (MixinExtras conflict)
re = r"module (mixinextras\.neoforge|MixinExtras) exports package [a-zA-Z0-9_.-]* to (mixinextras\.neoforge|MixinExtras)|Modules mixinextras\.neoforge and MixinExtras|Modules MixinExtras and mixinextras\.neoforge"
output = """Your log file indicates that you have two or more mods including conflicting versions of MixinExtras.
To fix this you can install this mod: https://www.curseforge.com/minecraft/mc-mods/mixin-extras-neoforge-on-forge-fix"""
print(search_content(re, content, output), end="")

#Problem 9.2 (MixinExtras incorrect inclusion)
re = r"Module (?:mixinextras\.neoforge|MixinExtras) contains package [a-zA-Z0-9_.-]+, module (?:mixinextras\.neoforge|MixinExtras) exports package [a-zA-Z0-9_.-]+ to (?:mixinextras\.neoforge|MixinExtras)|Modules MixinExtras and mixinextras\.neoforge export package|Modules mixinextras\.neoforge and MixinExtras export package"
output = """You have mods including a NeoForge specific version of MixinExtras on Forge.

Install [Mixin Extras NeoForge on Forge Fix](https://www.curseforge.com/minecraft/mc-mods/mixin-extras-neoforge-on-forge-fix)
This mod causes the NeoForge version to load an empty jar, preventing the crash."""
print(search_content(re, content, output), end="")

#Problem 10 (piracy not supported)
re = r"(?i)^(?=.*\btl(?:skin|_skin_)cape\b)(?!.*Error loading class: org/tlauncher/TLSkinCape).*$"
output = """Tlauncher references have been detected in the log file. It is a piracy supporting launcher and we do not provide support for it. Talking about or attempting to get support for it will result in a ban as per our rules.
See: https://discord.com/channels/428228256236306434/777323206884327484 #7"""
print(search_content(re, content, output), end="")

#Problem 11 (Xenon/Embeddium/Rubidium conflict)
re = r"(Mod ID: 'rubidium' from mod files: xenon)|(Mod ID: 'embeddium' from mod files: xenon)"
output = """It has been detected that the mod named `Xenon` has a conflict with other rendering mod(s) present.

`Xenon` is a fork of, and conflicts with, the mods named `Embeddium` and `Rubidium`.

> Of the mods named `Xenon`, `Embeddium`, `Rubidium` - you can only include one in a profile."""
print(search_content(re, content, output), end="")

#Problem 12 (maximum ID range)
re = "maximum id range exceeded"
output = "Your log looks to have a problem with the maximum number of IDs for something being already taken. To increase the limit to modern Minecraft's amounts, run the `!mc-idfix` command and follow the instructions"
print(search_content(re, content, output), end="")

#Problem 13 version 2 (Unsupported mods in profile -> advanced)
re = r"java\.lang\.UnsupportedClassVersionError(: ([a-zA-Z0-9_\.-]+(\/[a-zA-Z0-9_\.-]+)*) has been compiled by a more recent version of the Java Runtime \(class file version ([0-9]*\.[0-9]*)\), this version of the Java Runtime only recognizes class file versions up to ([0-9]*\.[0-9]*))?"
output = """You have a mod that is made for a different Java version, which indicates it is for a different Minecraft version.
The mod name is contained in the following path: `%GROUP2%`.

It has been compiled to Java Class version `%GROUP4%` but this Java Class version only supports `%GROUP5%`.

To fix this you should either remove the mod or find a version that is compatible, using the following list of versions

`Class version 52 - MC 1.16.5 and older
Class version 61 - MC 1.18 to 1.20.4
Class version 65 - MC 1.20.5 and newer
Class version 69 - MC 26.1 and newer`

In case this list does not contain a version, [Class to Java versions can be found here](https://javaalmanac.io/bytecode/versions/) and [Java to Minecraft versions here](https://minecraft.wiki/w/Tutorial:Update_Java#Why_update?)"""
print(search_content(re, content, output), end="")

#Problem 14 (MC launching with wrong videocard)
re = "Pixel format not accelerated"
output = """The message 'Pixel format not accelerated' was found in your log file.
This means that the game requires a dedicated graphics card be used with the game on launch.
- Check that your the current version of your graphics card drivers are up to date by using your card's installed driver update tool, or by visiting their website (use the following message command to get a website list):
!graphicsdrivers
- If, after trying to update graphics drivers the same message results, use the following message command and follow the instructions:
!mc-videocard"""
print(search_content(re, content, output), end="")

#Problem 15 (NBT too long)
re = r"(Tried to read NBT tag with too high complexity)|(Tried to read NBT tag that was too big)"
output = """For one reason or another you have objects in your world with NBT data with a depth greater than 512. For example, a backpack with too many items or too much NBT data.
You can add this mod to try and get around this limitation.
*(Note this is not a guarantee that it will work!)*

[Mod - Long NBT Killer](https://www.curseforge.com/minecraft/mc-mods/long-nbt-killer)"""
print(search_content(re, content, output), end="")

#Problem 16 (DH and Oculus/Iris not compatible)
re = r"ClassMetadataNotFoundException: com\.seibel\.distanthorizons\.coreapi\.util\.math\.Mat4f|MixinApplyError: Mixin \[mixins\.oculus\.compat\.dh\.json:NonCullingFrustumMixin\]"
output = "Versions of mods Distant Horizons and Oculus/Iris not compatible. Run command `!mc-dh` to see how to fix it."
print(search_content(re, content, output), end="")

#Problem 17 (pojavlauncher)
re = "pojavlaunch"
output = "We do not provide support for that launcher here, please reach out the the PojavLauncher devs for support"
print(search_content(re, content, output), end="")

#Problem 18 (important tag failing to load)
re = r"Couldn't load tag (minecraft:music_discs|minecraft:mineable/pickaxe|minecraft:mineable/axe|minecraft:mineable/shovel|minecraft:mineable/hoe|minecraft:needs_diamond_tool|minecraft:needs_iron_tool|minecraft:needs_stone_tool|minecraft:incorrect_for_wooden_tool|minecraft:incorrect_for_stone_tool|minecraft:incorrect_for_netherite_tool|minecraft:incorrect_for_iron_tool|minecraft:incorrect_for_gold_tool|minecraft:incorrect_for_diamond_tool|minecraft:enchantable/[a-z0-9_/]+|minecraft:[a-z0-9_]+_spawnable_on|minecraft:logs|minecraft:dolphin_located|minecraft:cats_spawn_in|minecraft:eye_of_ender_located|minecraft:infiniburn_end|minecraft:infiniburn_nether|neoforge:enchanting_fuels|neoforge:piglin_usable_crossbows|neoforge:pillager_usable_crossbows|neoforge:skeleton_usable_bows|neoforge:needs_netherite_tool|neoforge:villager_farmlands) as it is missing following references: ((?:\n\t)?(?:#?[a-z0-9_.-]+:[a-z0-9/_.-]+) \(from .*?\)(?:, )?)+"
output = """The tag `%GROUP1%` has failed to load. This tag controls important gameplay behaviour, so you should fix this.

The tag failed to load because of some missing entries due to straight up broken mods. You need to remove these mods:```%GROUP2%```
If these mods are absolutely required you can report the issue to the mod author then install [LMFT](https://www.curseforge.com/minecraft/mc-mods/lmft)."""
print(search_content(re, content, output), end="")

#Problem 19 (Legacy random source error debugging)
re = r"java\.lang\.IllegalStateException: Accessing LegacyRandomSource from multiple threads"
ouptut = """Some mod is accessing a single threaded resource from multiple threads, which breaks the game.

Please install https://www.curseforge.com/minecraft/mc-mods/uwrad-forge then cause the issue again and resend logs to make this easier to diagnose."""
print(search_content(re, content, output), end="")

#Problem 20 (malformed options.txt)
re = r"Duplicate key ([a-zA-Z0-9_.-]+) \(attempted merging values ([a-zA-Z0-9_.-]+) and ([a-zA-Z0-9_.-]+)\)"
output = """Your option.txt file has some duplicate entries, which causes (Neo)Forge to fail to load it.

The easiest way to fix this is to delete/rename your options.txt file. You could also manually edit it, removing one of these two lines:
```
%GROUP1%=%GROUP2%
%GROUP1%=%GROUP3%
```"""
print(search_content(re, content, output), end="")

#Problem 21 (client mod on server)
re = r"Failed to create mod instance. ModID: ([a-zA-Z0-9]+), class [a-zA-Z.]+\n+java\.lang\.BootstrapMethodError: java\.lang\.RuntimeException: Attempted to load class [a-zA-Z\/]+ for invalid dist [a-zA-Z_]+"
output = "Mod `%GROUP1%` is not meant to be loaded on server. Remove it to fix the crash."
print(search_content(re, content, output), end="")

#Problem 22 (broken mod)
re = r"Error during pre-loading phase: File mods\\(.+\.jar) is not a valid mod file"
output = """The mod `%GROUP1%` is broken and will not work until the mod author fixes it.
You should report the issue to the mod author and update, remove or downgrade it for now."""
print(search_content(re, content, output), end="")

#Experimental : possible solution for some crashes (failed to create mod instance)
re = r"Failed to create mod instance\. ModID: ([\w-]+), class [\w.]+"
output = "Mod `%GROUP1%` is not loading. Try updating it or removing it."
print(search_content(re, content, output), end="")

#Experimental : possible solution for some crashes (exception during event)
re = r"Caught exception during event [\w]+ dispatch for modid ([\w-]+)"
output = "Mod `%GROUP1%` is not loading. Try updating it or removing it."
print(search_content(re, content, output), end="")

#Experimental : detection of possible incompatibilities
re = r"Error during pre-loading phase: Mod (\w+) is incompatible with (\w+) ([\w.[\]()+-]+)\s+Currently, (\w+) is ([\w.[\]()+-]+)\s+The reason is: (\w+) supports (\w+) ([\w.[\]()+-]+) (and above|or below)"
output = "Mod `%GROUP1%` is incompatible with `%GROUP2%` version `%GROUP3%`. Currently, `%GROUP4%` is `%GROUP5%`. `%GROUP6%` supports `%GROUP7%` `%GROUP8%` %GROUP9%"
print(search_content(re, content, output), end="")

#Experimental : removing possibly broken mods
re = r"Suppressed: net\.minecraftforge\.fml\.ModLoadingException: ([\w' ]+) \([\w-]+\) encountered an error during the common_setup event phase"
output = "Mod %GROUP1% encountered an error during loading. Try updating it or removing it."
print(search_content(re, content, output), end="")

#Experimental : invalid mod IDs
re = r"Invalid modId found in file [A-Z]:(\\[\w*. -]+)*\\(.+\.jar,? ?) - ([\w' ]{2,64}) does not match the standard: \^\[a-z\]\[a-z0-9_\]\{1,63\}\$"
output = "Mod %GROUP3% has an invalid modId in its file (not matching standards). Try updating it or removing it."
print(search_content(re, content, output), end="")

#Experimental : missing mods in jar
re = r"net\.minecraftforge\.fml\.ModLoadingException: The Mod File [A-Z]:(?:\\[\w*. -]+)*\\(.+\.jar,? ?) has mods that were not found"
output = "Mod %GROUP1% has mods that were not found in its file. Try updating it or removing it."
print(search_content(re, content, output), end="")

#Experimental : possibly broken mods
re = r"Failed to register automatic subscribers\. ModID: ([\w-]+), class [\w.]+"
output = "Mod `%GROUP1%` is possibly broken. Try updating it or removing it."
print(search_content(re, content, output), end="")

#Experimental : incompatible version
#TODO : needs to be expanded
re = r"Mod .([a-zA-Z0-9]+). requires .([a-zA-Z0-9]+). or\n\s+.Currently, .([a-zA-Z0-9]+). is .([a-zA-Z0-9.+-]+)"
output = "Mod `%GROUP1%` requires `%GROUP2%`. Currently, `%GROUP4%` is `%GROUP5%`"

if not from_url:
	opened.close()

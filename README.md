# RetroArch Import Playlist

Adapt and import foreign RetroArch playlists into RetroArch

- Author: Tuncay D.
- Source: [Github](https://github.com/thingsiplay/retroarch-import-playlist)
- License: [MIT License](LICENSE)

## What is this for?

Sharing RetroArch playlist files with other users or environments is difficult.
That's mainly because those files contain hard coded file names and directory
paths, which may not match with your personal setup anymore. This command line
program will systematically replace those parts in the file, according to a set
of rules defined in a configuration file. Goal is to import someone else
RetroArch playlist file, to adapt and make them usable for your personal setup.

The script is limited and does not work in all cases. Missing Rom files or
those with different names won't match and are not playable, despite the
correct directory part. Simple cases such as Arcade games with standardized
names should work well to import. Compressed playlists are not supported.

## Install

No installation required. It's a Python script without additional requirements
other than Python itself. Download the .py script and run it.

```bash
git clone https://github.com/thingsiplay/retroarch-import-playlist
cd retroarch-import-playlist
chmod +x retroarch-import-playlist.py
```

This project is mainly tested under Linux, but should theoretically also work
on Windows.

## How to use

There is no GUI. Configure your personal configuration file and run the script
with the playlist file as input. According your configuration a new modified
file will be written to disk. The location to the new file is printed to
terminal.

```bash
$ ./retroarch-import-playlist.py "examples/playlists/Arcade - A-Z Uncommon Arcade Games.lpl"
/home/tuncay/Downloads/retroarch-import-playlist/Arcade - A-Z Uncommon Arcade Games.lpl
```

If you did not configure the settings, then you will most likely get an error
message without an output file. The error messages might look scary, that's
because I did not handle all cases. Read below how to configure correctly.

## Configuration file

In the config file, the `base_content_directory` points to your main Roms
folder. You need to add system rules with their associated Rom folder name. The
script will then combine `base_content_directory` and `content_directory` for
each system, so you don't need to repeat yourself. This project should come
with a skeleton file populated with most (if not all) system names already. You
just need to fill in those directories you care and have the Roms folder for.

### Location

The config file will be searched at some default locations in this order.
Whichever is found first will be loaded:

1. "SCRIPTNAME.ini" (_name and path of Python script, but with .ini extension_)
2. "~/.config/retroarch-import-playlist/default.ini" (_on Posix/Linux_)
   **or** "%LOCALAPPDATA%\retroarch-import-playlist\default.ini" (_on Windows_)

However, you can force to use a specific configuration file with command line
argument `-c FILE` . In this case default locations are ignored, even if the
specified file does not exist:

```bash
./retroarch-import-playlist.py -c rules/custom.ini
```

If no directory and extension parts are specified, then extension ".ini" is
assumed and file is searched in the config directory
"~/.config/retroarch-import-playlist/":

```bash
./retroarch-import-playlist.py -c default
```

### Example

```ini
[DEFAULT]
base_content_directory = ~/Emulation/Roms
core_directory = ~/.config/retroarch/cores
core_extension = so
output_directory = .
output_filename_prefix =
output_filename_append = .lpl
overwrite_existing_playlist = false
validate_rom_path = true

[MAME]
content_directory = mame

[Sega - Mega Drive - Genesis]
content_directory = megadrive

[Sega - Mega-CD - Sega CD]
content_directory = segacd

[Atari - 2600]
content_directory = atari2600
```

### Definition

`[DEFAULT]`

- `base_content_directory`: Location of your main Roms directory, which
  contains all the other sub folders specific for the systems. System specific
  folder names specified under "content_directory" are combined with this base.
- `core_directory`: Location where all Libretro cores are installed.
- `core_extension`: The file extension for the core to use, such as ".dll" or
  ".so" in example. The leading dot is optional and will be added automatically
  when needed.
- `output_directory`: Directory where to save the modified file. An empty entry
  defaults to original input files directory. A dot "." represents the current
  working directory you (or the script) are in.
- `output_filename_prefix`: Additional text to add in front of file name to
  save. Note, this is adding to the basename of the file.
- `output_filename_append`: Additional text to add after the file name. Note
  this setting also defines the file extension with the dot.
- `overwrite_existing_playlist`: Enable this to overwrite existing files when
  saving the modified playlist. Enable: `true`, `True`, `1` or `on` and disable:
  `false`, `False`, `0` or `off`
- `validate_rom_path`: Enable extra check if the Rom file does actually exist
  on the specified target directory. Do not include the game entry, if the Rom
  file cannot be located. Enable: `true`, `True`, `1` or `on` and disable:
  `false`, `False`, `0` or `off`

`[db_name]`

System rules. The section name `[db_name]` should be replaced with the actual
database name for the system, such as `[Atari - 2600]` . This system name can
be looked up under `"db_name":` for entries in the RetroArch .lpl playlist
file.

- `content_directory`: Roms folder for the associated system, such as
  "atari2600". This folder name will be automatically combined with
  `base_content_directory` defined in the `[DEFAULT]` section, to build the full
  path for this system.

## Create your own playlist for sharing

### RetroArch v1.19+

Since [RetroArch update version
1.19](https://www.libretro.com/index.php/retroarch-1-19-0-release/), the option
to create custom playlists was added. It might be disabled, so check and enable
at:

"Settings" > "User Interface" > "Menu Item Visibility" > "Quick Menu" > "Show
‘Add to Playlist’" and set it to `ON` .

Now in any playlist or in the Quick Menu while playing a game, the new option
"Add to Playlist" is available. Use it to your advantage.

### RetroArch v1.18 and earlier

In older versions of RetroArch, the "Add to Playlist" functionality is not
available. Therefore we have to be creative to create new playlists in a simple
manner. Here is a little step by step instructions to quickly create custom
playlists. It's basically just copying the Favorites file to your playlist
folder.

1. First go to your configuration directory of RetroArch, where all settings
   are stored. Remember this directory, it will be important later.
2. Rename the file "content_favorites.lpl" to preserve your current Favorites
   list. Or delete the file if you are careless.
3. Open RetroArch. Browse through all your playlists and have fun. If you click
   a game then there should be a menu entry "Add to Favorites". Add some games
   to the Favorites while you are at it.
4. Close RetroArch, as it gets late. No, just joking, but you need to close it
   ASAP!
5. Go to the RetroArch directory you were before.
6. Copy or move the "content_favorites.lpl" file to the "playlists" folder in
   the RetroArch directory.
7. Optionally rename it to something more useful which represents the content
   of the file, like "Arcade - Best games safe for work.lpl".

And that's basically it. Restart RetroArch and lookup if the new playlist is
working as expected. Now you are ready to share that file with the world and
set it under fire! Also tell them I sent you and don't forget to tell them
about this revolutionary script, so they can import your file as well and keep
history repeating itself.

## Download playlists

At this place I want to link to some sources with playlists, so you can
download and try them to import.

- [examples](examples/playlists)
- [lakka-playlists by balb](https://github.com/balb/lakka-playlists/tree/main/playlists)
  or [download a ZIP with all playlists](https://github.com/balb/lakka-playlists/raw/main/playlists.zip)

Just have in mind, random playlists are not guaranteed to work. Arcade
playlists are more likely to work than most console games with random file
names.

## See also

- doc: [ROMs, Playlists, and Thumbnails - Libretro Docs](https://docs.libretro.com/guides/roms-playlists-thumbnails/)
- app: [RetroArch Playlist Editor](https://www.marcrobledo.com/retroarch-playlist-editor/)
  / [Source](https://github.com/marcrobledo/retroarch-playlist-editor/)

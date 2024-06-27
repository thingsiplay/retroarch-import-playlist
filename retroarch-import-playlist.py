#!/usr/bin/env python3

import sys
import os
import pathlib
import json
import configparser
import argparse


def fullpath(path):
    if isinstance(path, pathlib.WindowsPath) or isinstance(
        path, pathlib.PureWindowsPath
    ):
        return pathlib.Path(path.as_posix())
    elif isinstance(path, str):
        if "\\" in path:
            return pathlib.Path(pathlib.PureWindowsPath(path).as_posix())
        else:
            return pathlib.Path(path).expanduser()
    else:
        return pathlib.Path(path).expanduser()


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Adapt and import foreign RetroArch playlists into RetroArch",
        epilog=(
            "Copyright © 2024 Tuncay D. <https://github.com/thingsiplay/retroarch-import-playlist>"
        ),
    )

    parser.add_argument("file", default=[], nargs="*", help=".lpl playlist input files")

    parser.add_argument(
        "-c",
        "--config",
        metavar="FILE",
        default=None,
        help="path to configuration file with rules for the script, if directory and file "
        "extension are not specified, then extension '.ini' is assumed and file is searched in "
        "scripts config directory",
    )

    parser.add_argument(
        "-o",
        "--output-directory",
        metavar="DIR",
        default=None,
        help="destination directory to save the modified files in",
    )

    return parser.parse_args()


def main():
    args = parse_arguments()
    if os.name == "nt":
        localappdata = os.getenv("LOCALAPPDATA")
        if localappdata:
            default_config_dir = (
                pathlib.Path(localappdata) / "retroarch-import-playlist"
            )
    else:
        default_config_dir = pathlib.Path("~/.config/").expanduser()
        default_config_dir = default_config_dir / "retroarch-import-playlist"

    if args.config:
        if "." in args.config or "/" in args.config or "\\" in args.config:
            config_locations = [fullpath(args.config)]
        else:
            config_locations = [
                default_config_dir / pathlib.Path(args.config).with_suffix(".ini")
            ]
    else:
        config_locations = [
            pathlib.Path(__file__).with_suffix(".ini"),
            default_config_dir / "default.ini",
        ]
    config = None
    for config_path in config_locations:
        if config_path.exists():
            config = configparser.ConfigParser()
            config.read(config_path)
            break
    if not config:
        raise FileNotFoundError(
            f"Configuration not found in possible locations: {[p.as_posix() for p in config_locations]}"
        )

    base_content_directory = fullpath(config["DEFAULT"]["base_content_directory"])
    core_directory = fullpath(config["DEFAULT"]["core_directory"])
    core_extension = config["DEFAULT"]["core_extension"]
    if not core_extension.startswith("."):
        core_extension = "." + core_extension
    output_filename_prefix = config["DEFAULT"]["output_filename_prefix"]
    output_filename_append = config["DEFAULT"]["output_filename_append"]
    overwrite_existing_playlist = config["DEFAULT"].getboolean(
        "overwrite_existing_playlist", False
    )
    validate_rom_path = config["DEFAULT"].getboolean("validate_rom_path", False)

    for file in args.file:
        input_path = fullpath(file)
        output_filename = (
            output_filename_prefix + input_path.stem + output_filename_append
        )
        if args.output_directory:
            output_directory = args.output_directory
        else:
            output_directory = config["DEFAULT"]["output_directory"]
        if output_directory == "":
            output_path = input_path.parent
        else:
            output_path = fullpath(output_directory)
        output_path = output_path / output_filename

        if not overwrite_existing_playlist and output_path.exists():
            continue

        with open(input_path, "r") as input_file:
            content = json.load(input_file)

            try:
                default_core_path = content["default_core_path"]
                if default_core_path:
                    default_core_path = fullpath(default_core_path)
                    default_core_path = default_core_path.with_suffix(
                        core_extension
                    ).name
                    default_core_path = core_directory / default_core_path
                    content["default_core_path"] = default_core_path.as_posix()
                else:
                    default_core_path = None
            except KeyError:
                default_core_path = None

            if "base_content_directory" in content:
                content["base_content_directory"] = fullpath(
                    base_content_directory
                ).as_posix()

            if "scan_content_dir" in content:
                del content["scan_content_dir"]

            for index, item in enumerate(content["items"]):
                db_name = item["db_name"].removesuffix(".lpl")

                if db_name in config.sections():
                    content_directory = fullpath(config[db_name]["content_directory"])
                    content_directory = base_content_directory / content_directory
                    if "path" in item:
                        path = fullpath(item["path"]).name
                        path = content_directory / path
                        if validate_rom_path and not path.exists():
                            del content["items"][index]
                            continue
                        content["items"][index]["path"] = path.as_posix()

                    core_path = None
                    if "core_path" in item:
                        if item["core_path"] != "DETECT" and item["core_path"] != "":
                            core_path = fullpath(item["path"]).name
                    elif default_core_path:
                        core_path = default_core_path.name

                    if core_path:
                        core_path = (
                            fullpath(item["core_path"]).with_suffix(core_extension).name
                        )
                        core_path = core_directory / core_path
                        content["items"][index]["core_path"] = core_path.as_posix()

            pathlib.Path(output_directory).mkdir(parents=True, exist_ok=True)
            output_path.touch(exist_ok=True)
            with open(output_path, "w") as output_file:
                json.dump(content, output_file, indent=2)
            if output_path.exists():
                print(output_path)


if __name__ == "__main__":
    sys.exit(main())

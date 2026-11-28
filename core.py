#----------------------------------------------------------------------
# Copyright (c) 2026 katzzotik | MIT License
# Repository: https://www.github.com/katzzotik/kMCSI
# Contact: katzzotik@proton.me

# NOT AN OFFICIAL MINECRAFT PRODUCT. THIS SOFTWARE IS NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT,
# OR ANY 3RD-PARTY MINECRAFT SERVER DEVELOPER, SUCH AS PAPERMC OR PURPURMC.
# IT IS A MINECRAFT SERVER INSTALL HELPER, AND DOES NOT CONTAIN OR DISTRIBUTE ANY OFFICIAL FILES,
# SUCH AS GAME, SERVER OR RUNTIME FILES. SERVER FILES ARE BEING DOWNLOADED FROM THEIR OFFICIAL SOURCES AT RUNTIME.
# THE USER MUST STILL ACCEPT THE MINECRAFT EULA TO RUN THE SERVER. IT DOES NOT ACCEPT THE EULA WITHOUT THE USER'S AGREEMENT.
# ALL TRADEMARKS, LOGOS, AND BRAND NAMES BELONG TO THEIR RESPECTIVE OWNERS.
# Server jars provided by PaperMC, PurpurMC (once added) and Mojang.
#----------------------------------------------------------------------

import ctypes
import os
import sys
import json
import shutil
import textwrap
import urllib.request
import urllib.error
import webbrowser
from pathlib import Path

if __name__ == "__main__":
    print("Please run main.py")
    sys.exit(0)

VERSION = "Alpha 0.1.0"

debug = False

# Defaults
DEFAULT_INSTALL_PATH = Path.home() / "mc-server"
DEFAULT_SERVER_JAR = "paper"
DEFAULT_SERVER_VERSION = "latest"
DEFAULT_SERVER_BUILD = "latest"
DEFAULT_MINECRAFT_EULA = False

# Selected
install_path = None
server_jar = None
server_version = None
server_build = None
minecraft_eula_agreement = False

# Cache
_cached_papermc_versions = None
_cached_papermc_builds = None

# Support for text color
text_color = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[94m",
    "gray": "\033[90m",
    "reset": "\033[0m",
}

# Available server jars
server_jars = [
    "paper",
    "purpur",
    "vanilla",
]

# User Agent header for API
global_kMCSI_api_headers = {
    "User-Agent": f"katzzotikz-MC-Server-Installer/{VERSION} (https://github.com/katzzotik/kMCSI)"
}

def fix_conhost_text_color():
    if os.name == "nt":
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_ulong()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING

def copyright_notice():
    print(f"{text_color["yellow"]}Copyright (c) 2026 katzzotik | MIT License{text_color["reset"]}")
    print(f"{text_color["yellow"]}Repository: https://www.github.com/katzzotik/kMCSI{text_color["reset"]}")
    print(f"{text_color["yellow"]}Contact: katzzotik@proton.me{text_color["reset"]}")
    print(
        f"{text_color["red"]}"
        "\nNOT AN OFFICIAL MINECRAFT PRODUCT. THIS SOFTWARE IS NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT,\n"
        "OR ANY 3RD-PARTY MINECRAFT SERVER DEVELOPER, SUCH AS PAPERMC OR PURPURMC.\n"
        "IT IS A MINECRAFT SERVER INSTALL HELPER, AND DOES NOT CONTAIN OR DISTRIBUTE ANY OFFICIAL FILES,\n"
        "SUCH AS GAME, SERVER OR RUNTIME FILES. SERVER FILES ARE BEING DOWNLOADED FROM THEIR OFFICIAL SOURCES AT RUNTIME.\n"
        "THE USER MUST STILL ACCEPT THE MINECRAFT EULA TO RUN THE SERVER.\nIT DOES NOT ACCEPT THE EULA WITHOUT THE USER'S AGREEMENT.\n"
        "ALL TRADEMARKS, LOGOS, AND BRAND NAMES BELONG TO THEIR RESPECTIVE OWNERS."
        f"{text_color["reset"]}"
    )
    print(f"{text_color["yellow"]}Server jars provided by PaperMC(papermc.io), PurpurMC(purpurmc.org) (once added) and Mojang(minecraft.net) (as backbone for paper).{text_color["reset"]}\n")

def get_install_path_from_user() -> Path:
    print(f"Please select a location to install the server to.\nDefault: {DEFAULT_INSTALL_PATH}")

    while True:
        target_dir = None

        try: 
            user_input = input(f"{text_color["gray"]}Leave empty for default> {text_color["yellow"]}").strip()
        finally:
            print(text_color["reset"], end="")

        if not user_input:
            target_dir = DEFAULT_INSTALL_PATH
        else:
            target_dir = Path(user_input).expanduser().resolve()

        if target_dir.exists() and not target_dir.is_dir():
            print(f"{text_color["red"]}[ERROR] {target_dir} is a file, not a directory.{text_color["reset"]}")
            continue
        elif target_dir.exists() and any(target_dir.iterdir()):
            print(f"{text_color["red"]}[ERROR] {target_dir} is not empty.{text_color["reset"]}")
            continue
        
        print(f"{text_color["gray"]}[LOG] Installing to: {target_dir}\n{text_color["reset"]}")
        return target_dir

def get_server_jar_from_user():
    print(f"Please specify the server jar you would like to use. Type list for all options.\nDefault: {DEFAULT_SERVER_JAR.capitalize()}")

    while True:
        target_server_jar = None

        try: 
            user_input = input(f"{text_color["gray"]}Leave empty for default> {text_color["yellow"]}").strip().lower()
        finally:
            print(text_color["reset"], end="")

        if not user_input:
            user_input = DEFAULT_SERVER_JAR
        elif user_input == "list":
            for index, jar in enumerate(server_jars, start=1):
                print(f"{index}. {jar.capitalize()}")
            continue
        
        if user_input.isdigit():
            index = int(user_input) - 1
            if 0 <= index < len(server_jars):
                user_input = server_jars[index]
        
        if user_input in server_jars:
            if user_input == "paper":
                target_server_jar = "paper"
        else:
            print(f"{text_color["red"]}[ERROR] Unknown server jar.{text_color["reset"]}")
            continue
        if not target_server_jar:
            print(f"{text_color["gray"]}[LOG] {user_input.capitalize()} is not supported yet, but it's in the works!{text_color["reset"]}")
            continue
        else:
            print(f"{text_color["gray"]}[LOG] {target_server_jar.capitalize()} selected.{text_color["reset"]}")
            return target_server_jar

def fetch_papermc_versions(force_refresh=False):
    global _cached_papermc_versions
    
    if _cached_papermc_versions is not None and not force_refresh:
        if debug:
            print(f"{text_color["gray"]}[DEBUG] Using cached PaperMC versions{text_color["reset"]}")
        return _cached_papermc_versions
    
    try:
        url = "https://fill.papermc.io/v3/projects/paper/versions"
        req = urllib.request.Request(url, headers=global_kMCSI_api_headers)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
            
        supported_versions = []
        unsupported_versions = []

        for v in data["versions"]:
            if v["version"]["support"]["status"] == "SUPPORTED":
                supported_versions.append(v["version"]["id"])

        for v in data["versions"]:
            if v["version"]["support"]["status"] == "UNSUPPORTED":
                unsupported_versions.append(v["version"]["id"])

        _cached_papermc_versions = (supported_versions, unsupported_versions)
        if debug:
            print(f"{text_color["gray"]}[DEBUG] PaperMC Versions were fetched from API and cached{text_color["reset"]}")
        return supported_versions, unsupported_versions
    except urllib.error.URLError:
        print(f"{text_color["red"]}[ERROR] urllib encountered an URLError! Is the server reachable? Are you connected to the internet?{text_color["reset"]}")
        return ""
    except urllib.error.HTTPError:
        print(f"{text_color["red"]}[ERROR] urllib encountered an HTTPError! There seems to be a problem on the server side.{text_color["reset"]}")
        return ""
    except urllib.error.ContentTooShortError:
        print(f"{text_color["red"]}[ERROR] urllib encountered an ContentTooShortError!{text_color["reset"]}")
        return ""
    except Exception as e:
        print(f"{text_color["red"]}[ERROR] Unexpected Error: ({type(e).__name__}):{e}{text_color["reset"]}")

def list_papermc_versions():
    try:
        paper_supported, paper_unsupported = fetch_papermc_versions()

        print_supported = ", ".join(paper_supported)
        print_unsupported = ", ".join(paper_unsupported)

        terminal_width = shutil.get_terminal_size().columns
        
        print_supported_wrapped = textwrap.fill(print_supported, width=terminal_width)
        print_unsupported_wrapped = textwrap.fill(print_unsupported, width=terminal_width)

        print(f"{text_color["green"]}Supported:")
        #print(", ".join(paper_supported))
        print(print_supported_wrapped)

        print(f"{text_color["red"]}Unsupported (no updates from PaperMC, but selectable):")
        #print(", ".join(paper_unsupported))
        print(print_unsupported_wrapped)

        print(f"{text_color["reset"]}", end="")
    except Exception:
        print(f"{text_color["red"]}[ERROR] It seems the API did not return any available versions.{text_color["reset"]}")

def get_server_version_from_user():
    if server_jar == "paper":
        fetch_papermc_versions()

    print(f"Please choose the server version you would like to use. Type list for all options.\nDefault: {DEFAULT_SERVER_VERSION} ({fetch_papermc_versions()[0][0]})")
    
    while True:
        try: 
            user_input = input(f"{text_color["gray"]}Leave empty for default> {text_color["yellow"]}").strip().lower()
        finally:
            print(text_color["reset"], end="")
        
        if server_jar == "paper":
            if user_input == "list":
                list_papermc_versions()
                continue
            elif user_input == "refresh":
                fetch_papermc_versions(force_refresh=True)
                print(f"{text_color["gray"]}[LOG] Refetched from API.{text_color["reset"]}")
                continue
            elif not user_input or user_input == "latest":
                target_server_version = fetch_papermc_versions()[0][0]
            elif any(user_input in group for group in fetch_papermc_versions()):
                target_server_version = user_input
            else:
                print(f"{text_color["red"]}[ERROR] Unknown server version.{text_color["reset"]}")
                continue


        print(f"{text_color["gray"]}[LOG] {target_server_version} selected.{text_color["reset"]}")
        return target_server_version

def fetch_papermc_builds(force_refresh=False):
    global _cached_papermc_builds

    try:
        if _cached_papermc_builds is not None and not force_refresh:
            if debug:
                print(f"{text_color["gray"]}[DEBUG] Using cached PaperMC builds{text_color["reset"]}")
            return _cached_papermc_builds

        url = f"https://fill.papermc.io/v3/projects/paper/versions/{server_version}/builds"
        req = urllib.request.Request(url, headers=global_kMCSI_api_headers)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))

        papermc_server_builds = []

        for v in data:
            papermc_server_builds.append(v["id"])

        papermc_server_builds_str = list(map(str, papermc_server_builds))

        _cached_papermc_builds = papermc_server_builds_str
        if debug:
            print(f"{text_color["gray"]}[DEBUG] PaperMC builds were fetched from API and cached{text_color["reset"]}")
        return papermc_server_builds_str

    except urllib.error.URLError:
        print(f"{text_color["red"]}[ERROR] urllib encountered an URLError! Is the server reachable? Are you connected to the internet?{text_color["reset"]}")
        return ""
    except urllib.error.HTTPError:
        print(f"{text_color["red"]}[ERROR] urllib encountered an HTTPError! There seems to be a problem on the server side.{text_color["reset"]}")
        return ""
    except urllib.error.ContentTooShortError:
        print(f"{text_color["red"]}[ERROR] urllib encountered an ContentTooShortError!{text_color["reset"]}")
        return ""
    except Exception as e:
        print(f"{text_color["red"]}[ERROR] Unexpected Error: ({type(e).__name__}):{e}{text_color["reset"]}")

def list_papermc_builds():
    try:
        latest_paper_build = fetch_papermc_builds()[0]
        other_paper_builds = fetch_papermc_builds()[1:]

        print_other_builds = ", ".join(other_paper_builds)

        terminal_width = shutil.get_terminal_size().columns
        
        print_other_builds_wrapped = textwrap.fill(print_other_builds, width=terminal_width)

        print(f"{text_color["green"]}Latest build:")
        print(latest_paper_build)

        print(f"{text_color["red"]}Older builds:")
        print(print_other_builds_wrapped)
        print(f"{text_color["reset"]}", end="")
    except Exception as e:
        print(f"{text_color["red"]}[ERROR] It seems the API did not return any available versions.{e}{text_color["reset"]}")

def get_server_build_from_user():
    if server_jar == "paper":
        fetch_papermc_builds()

    print(f"Please choose the server build you would like to use. Type list for all options.\nDefault: {DEFAULT_SERVER_BUILD} ({fetch_papermc_builds()[0]})")

    while True:
        try: 
            user_input = input(f"{text_color["gray"]}Leave empty for default> {text_color["yellow"]}").strip().lower()
        finally:
            print(text_color["reset"], end="")
        
        if server_jar == "paper":
            if user_input == "list":
                list_papermc_builds()
                continue
            elif user_input == "refresh":
                fetch_papermc_builds(force_refresh=True)
                print(f"{text_color["gray"]}[LOG] Refetched from API.{text_color["reset"]}")
                continue
            elif not user_input or user_input == "latest":
                target_server_build = fetch_papermc_builds()[0]
            elif user_input in fetch_papermc_builds():
                target_server_build = user_input
            else:
                print(f"{text_color["red"]}[ERROR] Unknown server build.{text_color["reset"]}")
                continue


        print(f"{text_color["gray"]}[LOG] {target_server_build} selected.{text_color["reset"]}")
        return target_server_build

def get_eula_agreement_from_user():
    print(f"{text_color["red"]}NOT AN OFFICIAL MINECRAFT PRODUCT. kMCSI IS NOT AFFILIATED WITH MOJANG OR MICROSOFT.{text_color["reset"]}")
    print(f"In order to run the server, you must agree to the Minecraft EULA (https://www.minecraft.net/eula). If you do not agree, the server will not run, but still install. \nThis can be changed anytime in eula.txt. Type \"link\" to open the Minecraft EULA webpage.")

    local_minecraft_eula_agreement = False

    while True:
        try: 
            user_input = input(f"{text_color["gray"]}Do you agree? [Y/n/link]> {text_color["yellow"]}").strip().lower()
        finally:
            print(text_color["reset"], end="")
        
        if user_input in ("y", "yes"):
            local_minecraft_eula_agreement = True
        elif user_input in ("n", "no"):
            local_minecraft_eula_agreement = False
        elif user_input == "link":
            webbrowser.open_new_tab("https://www.minecraft.net/eula")
            continue
        else:
            print(f"{text_color["red"]}[ERROR] Unknown option.{text_color["reset"]}")
            continue
        
        if local_minecraft_eula_agreement == True:
            print(f"{text_color["gray"]}[LOG] You have agreed to the Minecraft EULA.{text_color["reset"]}")
        else:
            print(f"{text_color["gray"]}[LOG] You have not agreed to the Minecraft EULA. \n[LOG] In order to run the server, you must manually edit eula.txt and agree.{text_color["reset"]}")
        return local_minecraft_eula_agreement
        
def user_option_review():
    print(
        "Please review your options before installing:\n"
        f"Installing to: {install_path}\n"
        f"Server jar: {server_jar.capitalize()}\n"
        f"├── Server version: {server_version}\n"
        f"└── Server build: {server_build}\n"
        f"Minecraft EULA Agreement: {minecraft_eula_agreement}"
    )
    while True:
        try: 
            user_input = input(f"{text_color["gray"]}Ready to install [Y/n]?> {text_color["yellow"]}").strip().lower()
        finally:
            print(text_color["reset"], end="")

        if user_input in ("y", "yes"):
            return
        elif user_input in ("n", "no"):
            print(f"{text_color["gray"]}[LOG] Installation cancelled.{text_color["reset"]}")
            sys.exit(0)
        else:
            print(f"{text_color["red"]}[ERROR] Unknown option.{text_color["reset"]}")
            continue

def install():
    print("This program isnt finished yet.")
    return
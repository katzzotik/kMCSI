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

import core
from pathlib import Path

try:
    print(f"{core.text_color["blue"]}Welcome to kMCSI Version {core.VERSION}!{core.text_color["reset"]}")
    core.copyright_notice()

    # Define
    install_path = None
    server_jar = None
    minecraft_version = None

    print(f"Please select a location to install the server to.\nDefault: {core.DEFAULT_INSTALL_PATH}")
    install_path = core.get_install_path()
    print(f"{core.text_color["gray"]}[LOG] Installing to: {install_path}\n{core.text_color["reset"]}")

    print(f"Please specify the server jar would you like to use. Type list for all options.\nDefault: {core.DEFAULT_SERVER_JAR.capitalize()}")
    server_jar = core.get_server_jar()


except KeyboardInterrupt:
    print(f"{core.text_color["reset"]}\n{core.text_color["gray"]}[LOG] Installation canceled by user.{core.text_color["reset"]}")
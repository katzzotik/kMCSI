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
from core import text_color

# Fix color issues on windows conhost
core.fix_conhost_text_color()

try:
    print(f"{text_color["blue"]}Welcome to kMCSI Version {core.VERSION}!{text_color["reset"]}")
    core.copyright_notice()

    print(f"Please select a location to install the server to.\nDefault: {core.DEFAULT_INSTALL_PATH}")
    core.install_path = core.get_install_path_from_user()

    print(f"Please specify the server jar you would like to use. Type list for all options.\nDefault: {core.DEFAULT_SERVER_JAR.capitalize()}")
    core.server_jar = core.get_server_jar_from_user()

    print(f"Please choose the server version you would like to use. Type list for all options.\nDefault: {core.DEFAULT_SERVER_VERSION}")
    core.server_version = core.get_server_version_from_user()


except KeyboardInterrupt:
    print(f"{text_color["reset"]}\n{text_color["gray"]}[LOG] Installation canceled by user.{text_color["reset"]}")
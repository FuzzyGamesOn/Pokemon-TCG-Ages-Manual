# normally, this file is empty. 
# but when we want something to run automatically (like registering our custom client), we want to do it in this file.

from worlds.LauncherComponents import Component, components, launch_subprocess

def launch_client(*args):
    from .client import launch as Main
    launch_subprocess(Main, name="Manual PokemonTCGAges client")

def add_client_to_launcher() -> None:
    components.append(Component("Manual PokemonTCGAges Client", "ManualPTCGAClient", func=launch_client))

add_client_to_launcher()
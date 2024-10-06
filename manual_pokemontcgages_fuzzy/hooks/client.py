import asyncio
import re
import json

from CommonClient import get_base_parser, server_loop
from ..ManualClient import read_apmanual_file, ManualContext, tracker_loaded, gui_enabled, game_watcher_manual
from .functions import get_pack_names, get_unique_evos, get_energy_cards, \
    get_card_picture, get_evo_picture, get_enemy_picture

game_name = "Manual_PokemonTCGAges_Fuzzy"
client_name = "Archipelago Manual (PokemonTCGAges) Client"
client_description = "Manual PokemonTCGAges Client, for operating the Manual game named PokemonTCGAges in Archipelago."

def get_context(args, config_file):
    return ManualPokemonTCGAgesContext(args.connect, args.password, config_file.get("game"), config_file.get("player_name"))

class ManualPokemonTCGAgesContext(ManualContext):
    game = game_name # set the game name to change the Manual Game ID field
    
    def after_run_gui(self):
        # add a custom tab to the client named "Deck Builder"
        self.ui.logging_pairs.append(
            ("Deck Builder", "Deck Builder")
        )
        self.ui.base_title = client_name # set a custom title for the custom client window

        self.last_deck_contents = []
        self.enemies = {}

    def on_package(self, cmd: str, args: dict):
        super().on_package(cmd, args)

        if cmd in {"Connected"}:
            self.enemies = json.loads(args['slot_data'].get('enemies', "{}"))

            self.update_custom_ui()
        elif cmd in {"DataPackage", "ReceivedItems", "RoomUpdate"}:
            self.update_custom_ui()

    def update_custom_ui(self):
        from kivy.uix.modalview import ModalView
        from kivy.uix.scrollview import ScrollView
        from kivy.uix.gridlayout import GridLayout
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.spinner import Spinner, SpinnerOption
        from kivy.uix.button import Button
        from kivy.uix.image import AsyncImage
        from kivy.metrics import dp

        # Spinner means Dropdown, because Kivy. And Dropdown is a pita to use
        class CardSelect(Spinner): 
            background_color = [4/255, 121/255, 217/255, 1] # colors are rgba, so rgb (1-255) and an opacity

        class EnergySelect(CardSelect): # extend CardSelect in case we add default behavior later
            background_color = [48/255, 138/255, 34/255, 1]

        class EnemySelect(CardSelect): # extend CardSelect in case we add default behavior later
            background_color = [255/255, 28/255, 40/255, 1]

        class CardSelectOption(SpinnerOption):
            background_color = [163/255, 127/255, 93/255, 1]
        
        class ViewButton(Button): # kivy gets angry when i move all the args here, for some gd reason
            background_color = [255/255, 220/255, 41/255, 1]

        def show_card_preview(url: str):
            if not url:
                return
            
            card_preview.source = url
            card_preview.size = (dp(300), dp(400))
            
            card_preview_layout.open()

        def hide_card_preview():
            card_preview.source = "https://static.vecteezy.com/system/resources/thumbnails/001/826/199/small_2x/progress-loading-bar-buffering-download-upload-and-loading-icon-vector.jpg"
            card_preview.size = (dp(0), dp(0))

            card_preview_layout.dismiss()

        def copy_enemy_decklist(enemy_listing: str):
            from kivy.core.clipboard import Clipboard

            card_name = enemy_listing.split(': ')[1].strip()
            deck_list = f"60 {card_name}"

            Clipboard.copy(deck_list)

        def add_card_to_contents(card_name: str):
            hide_card_preview()

            if card_name == "(None Selected)":
                return
            
            if is_deck_full():
                return

            card_entry = None

            for _, child in enumerate(deck_contents.children):
                if card_entry is not None:
                    break

                for _, card_child in enumerate(child.children):
                    if type(card_child) is Label and card_name in card_child.text:
                        card_entry = child
                        break

            if card_entry is None:
                card_entry = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(22))
                deck_contents.add_widget(card_entry)

                card_entry_label = Label(text=f"0 {card_name}", size=(dp(250), dp(20)), text_size=(dp(250), dp(20)), size_hint_y=None, size_hint_x=None, valign='middle')
                card_entry_minus = Button(text="-", size_hint=(None, None), size=(dp(30), dp(20)))
                card_entry_minus.bind(on_release=lambda _: minus_quantity(card_entry))
                card_entry_plus = Button(text="+", size_hint=(None, None), size=(dp(30), dp(20)))
                card_entry_plus.bind(on_release=lambda _: plus_quantity(card_entry))

                card_entry.add_widget(card_entry_label)
                card_entry.add_widget(card_entry_minus)
                card_entry.add_widget(card_entry_plus)

            plus_quantity(card_entry)

        def minus_quantity(card_entry: BoxLayout):
            for _, child in enumerate(card_entry.children):
                if type(child) is Label:
                    label_quantity = int(child.text.split(" ")[0].strip())
                    new_label_quantity = label_quantity - 1

                    # if we're reducing quantity by 1 and it becomes 0, remove the card from the list entirely
                    if new_label_quantity < 1:
                        deck_contents.remove_widget(card_entry)
                        return

                    child.text = re.sub('^\d+\s', f"{new_label_quantity} ", child.text)

            update_total_quantity()

        def plus_quantity(card_entry: BoxLayout):
            if is_deck_full():
                return
            
            for _, child in enumerate(card_entry.children):
                if type(child) is Label:
                    label_quantity = int(child.text.split(" ")[0].strip())
                    new_label_quantity = label_quantity + 1

                    # if we're increasing quantity by 1 and it is higher than 4 and not a basic energy card, just return -- no increases beyond 4
                    if new_label_quantity > 4 and len([energy for energy in all_energy_cards if energy in child.text]) == 0:
                        return

                    child.text = re.sub('^\d+\s', f"{new_label_quantity} ", child.text)
            
            update_total_quantity()

        def update_total_quantity():
            self.last_deck_contents = []
            total = 0

            for _, child in enumerate(deck_contents.children):
                for _, card_child in enumerate(child.children):
                    if type(card_child) is Label:
                        self.last_deck_contents.append(card_child.text)
                        total += int(card_child.text.split(' ')[0].strip())
                        
            card_total.text = f"{total} Cards in Deck"

        def is_deck_full():
            return int(card_total.text.split(' ')[0].strip()) >= 60

        def copy_contents():
            from kivy.core.clipboard import Clipboard

            deck_cards_list = []

            for _, child in enumerate(deck_contents.children):
                for _, card_child in enumerate(child.children):
                    if type(card_child) is Label:
                        deck_cards_list.append(card_child.text)

            deck_cards_list.reverse() # for some reason, it captures the cards in reverse order from how they're displayed

            deck_list = "\n".join(deck_cards_list)
            Clipboard.copy(deck_list)

        def clear_contents():
            deck_contents.clear_widgets()
            update_total_quantity()
            self.last_deck_contents = []

        deck_builder_layout = GridLayout(cols=2)
        card_picker_layout = BoxLayout(orientation="vertical", padding=(dp(20), dp(20), dp(20), dp(50))) # padding is (left, top, right, bottom)
        deck_builder_layout.add_widget(card_picker_layout)

        ###
        # Dropdown for received cards
        ###

        received_cards_layout = BoxLayout(orientation="vertical", size_hint=(None, None), size=(dp(300), dp(100)))
        received_cards_controls = BoxLayout(orientation="horizontal", size_hint=(None, None), size=(dp(300), dp(40)), padding=(0, dp(5)), spacing=dp(5))

        card_dropdown_label = Label(text="Received Card", size_hint_x=None, bold=True)
        received_cards_layout.add_widget(card_dropdown_label)

        unlocked_cards = [
            self.item_names[network_item.item] for network_item in self.items_received
        ]
        
        received_card_picker = CardSelect(text="(None Selected)", size_hint=(None, None), size=(dp(250), dp(30)), sync_height=True,
            values=unlocked_cards, option_cls=CardSelectOption)

        card_dropdown_btn = Button(text="Add", size_hint=(None, None), size=(dp(50), dp(30)))
        card_dropdown_btn.bind(on_release=lambda _: add_card_to_contents(received_card_picker.text))
        card_dropdown_view_btn = ViewButton(text="View Card", size_hint=(None, None), size=(dp(100), dp(30)))
        card_dropdown_view_btn.bind(on_release=lambda _: show_card_preview(get_card_picture(received_card_picker.text)))
        
        received_cards_controls.add_widget(card_dropdown_btn)
        received_cards_controls.add_widget(card_dropdown_view_btn)
        received_cards_layout.add_widget(received_card_picker)
        received_cards_layout.add_widget(received_cards_controls)
        
        card_picker_layout.add_widget(received_cards_layout)

        ###
        # Dropdown for pre-evolution cards
        ###

        evolution_cards_layout = BoxLayout(orientation="vertical", size_hint=(None, None), size=(dp(300), dp(100)))
        evolution_cards_controls = BoxLayout(orientation="horizontal", size_hint=(None, None), size=(dp(300), dp(40)), padding=(0, dp(5)), spacing=dp(5))

        evo_dropdown_label = Label(text="Pre-Evolution Card", size=(dp(130), dp(30)), size_hint_y=None, size_hint_x=None, bold=True)
        evolution_cards_layout.add_widget(evo_dropdown_label)

        evolution_cards = [
            evo_name for pack in get_pack_names() for evo_name in get_unique_evos(pack)
        ]
        
        evolution_card_picker = CardSelect(text="(None Selected)", size_hint=(None, None), size=(dp(250), dp(30)), sync_height=True,
            values=evolution_cards, option_cls=CardSelectOption)

        evo_dropdown_btn = Button(text="Add", size_hint=(None, None), size=(dp(50), dp(30)))
        evo_dropdown_btn.bind(on_release=lambda _: add_card_to_contents(evolution_card_picker.text))
        evo_dropdown_view_btn = ViewButton(text="View Card", size_hint=(None, None), size=(dp(100), dp(30)))
        evo_dropdown_view_btn.bind(on_release=lambda _: show_card_preview(get_evo_picture(evolution_card_picker.text)))
        
        evolution_cards_controls.add_widget(evo_dropdown_btn)
        evolution_cards_controls.add_widget(evo_dropdown_view_btn)
        evolution_cards_layout.add_widget(evolution_card_picker)
        evolution_cards_layout.add_widget(evolution_cards_controls)
        
        card_picker_layout.add_widget(evolution_cards_layout)

        ###
        # Dropdown for energy cards
        ###

        energy_cards_layout = BoxLayout(orientation="vertical", size_hint=(None, None), size=(dp(300), dp(100)))
        energy_cards_controls = BoxLayout(orientation="horizontal", size_hint=(None, None), size=(dp(300), dp(40)), padding=(0, dp(5)), spacing=dp(5))

        energy_dropdown_label = Label(text="Basic Energy Card", size=(dp(130), dp(30)), size_hint_y=None, size_hint_x=None, bold=True)
        energy_cards_layout.add_widget(energy_dropdown_label)

        all_energy_cards = [
            energy_name for pack in get_pack_names() for energy_name in get_energy_cards(pack)
        ]
        
        energy_card_picker = EnergySelect(text="(None Selected)", size_hint=(None, None), size=(dp(250), dp(30)), sync_height=True,
            values=all_energy_cards, option_cls=CardSelectOption)

        energy_dropdown_btn = Button(text="Add", size_hint=(None, None), size=(dp(50), dp(30)))
        energy_dropdown_btn.bind(on_release=lambda _: add_card_to_contents(energy_card_picker.text))
        
        energy_cards_controls.add_widget(energy_dropdown_btn)
        energy_cards_layout.add_widget(energy_card_picker)
        energy_cards_layout.add_widget(energy_cards_controls)
        
        card_picker_layout.add_widget(energy_cards_layout)

        ###
        # Dropdown for enemy cards
        ###

        enemy_cards_layout = BoxLayout(orientation="vertical", size_hint=(None, None), size=(dp(300), dp(100)))
        enemy_cards_controls = BoxLayout(orientation="horizontal", size_hint=(None, None), size=(dp(300), dp(40)), padding=(0, dp(5)), spacing=dp(5))

        enemy_dropdown_label = Label(text="Enemies by HP", size=(dp(110), dp(30)), size_hint_y=None, size_hint_x=None, bold=True)
        enemy_cards_layout.add_widget(enemy_dropdown_label)

        enemy_cards = [
            f"{enemy_hp} HP: {enemy_card}" for enemy_hp, enemy_card in self.enemies.items()
        ]
        
        enemy_card_picker = EnemySelect(text="(None Selected)", size_hint=(None, None), size=(dp(250), dp(30)), sync_height=True,
            values=enemy_cards, option_cls=CardSelectOption)

        enemy_dropdown_btn = Button(text="Copy Decklist", size_hint=(None, None), size=(dp(150), dp(30)))
        enemy_dropdown_btn.bind(on_release=lambda _: copy_enemy_decklist(enemy_card_picker.text))
        enemy_dropdown_view_btn = ViewButton(text="View Card", size_hint=(None, None), size=(dp(100), dp(30)))
        enemy_dropdown_view_btn.bind(on_release=lambda _: show_card_preview(get_enemy_picture(enemy_card_picker.text.split(':')[1].strip())))
        
        enemy_cards_controls.add_widget(enemy_dropdown_btn)
        enemy_cards_controls.add_widget(enemy_dropdown_view_btn)
        enemy_cards_layout.add_widget(enemy_card_picker)
        enemy_cards_layout.add_widget(enemy_cards_controls)
        
        card_picker_layout.add_widget(enemy_cards_layout)

        ###
        # Right sidebar for deck contents once picked/added
        ###

        deck_contents_layout = BoxLayout(orientation="vertical", padding=dp(20))
        deck_controls = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(22))
        deck_contents_scrollable = ScrollView(do_scroll=(False, True), bar_width=10)
        deck_contents = BoxLayout(orientation="vertical", size_hint_y=None, padding=(0, dp(20)))
        deck_contents.bind(minimum_height = deck_contents.setter('height'))
        deck_contents_scrollable.add_widget(deck_contents)

        card_total = Label(text="0 Cards in Deck", size=(dp(120), dp(20)), text_size=(dp(120), dp(20)), size_hint_y=None, size_hint_x=None, valign='middle', bold=True)
        export_btn = Button(text="Export to Clipboard", size_hint=(None, None), size=(dp(150), dp(20)))
        export_btn.bind(on_release=lambda _: copy_contents())
        clear_btn = Button(text="Clear Deck", size_hint=(None, None), size=(dp(80), dp(20)))
        clear_btn.bind(on_release=lambda _: clear_contents())

        deck_controls.add_widget(card_total)
        deck_controls.add_widget(export_btn)
        deck_controls.add_widget(clear_btn)

        deck_contents_layout.add_widget(deck_controls)
        deck_contents_layout.add_widget(deck_contents_scrollable)
        
        deck_builder_layout.add_widget(deck_contents_layout)

        # used by *_card_preview methods above
        card_preview_layout = ModalView(size_hint=(None, None), size=(300, 400))
        card_preview = AsyncImage(size_hint=(None, None))
        card_preview_layout.add_widget(card_preview)

        for child in self.ui.tabs.tab_list:
            if child.text == "Deck Builder":
                child.background_color = [117/255, 177/255, 240/255, 1]
                panel = child # instead of creating a new TabbedPanelItem, use the one we use above to make the tabs show

        panel.content = deck_builder_layout

        # now, check for a pre-existing deck and restore it (since it's cleared when a check is sent)
        if len(self.last_deck_contents) > 0:
            reversed_deck_contents = [card for card in self.last_deck_contents] # copies the list
            reversed_deck_contents.reverse()

            for deck_listing in reversed_deck_contents:
                qty = int(deck_listing.split(" ")[0].strip())
                card_name = " ".join(deck_listing.split(" ")[1:]).strip()

                for _ in range(qty):
                    add_card_to_contents(card_name)

#######################################################
########### End of *ManualContext class ###############
#######################################################




#################################################################
# The below is copied from the Manual client with minimal changes. 
# Leave it alone unless you know what you're doing.
#################################################################

async def main(args):
    config_file = {}
    if args.apmanual_file:
        config_file = read_apmanual_file(args.apmanual_file)
    ctx = get_context(args, config_file)
    ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")

    ctx.item_table = config_file.get("items", {})
    ctx.location_table = config_file.get("locations", {})
    ctx.region_table = config_file.get("regions", {})
    ctx.category_table = config_file.get("categories", {})

    if tracker_loaded:
        ctx.run_generator()

    if gui_enabled:
        ctx.run_gui()
        ctx.after_run_gui()

    ctx.run_cli()

    progression_watcher = asyncio.create_task(
        game_watcher_manual(ctx), name="ManualProgressionWatcher")

    await ctx.exit_event.wait()
    ctx.server_address = None

    await progression_watcher

    await ctx.shutdown()

def launch() -> None:
    import colorama

    parser = get_base_parser(description=client_description)
    parser.add_argument('apmanual_file', default="", type=str, nargs="?",
                        help='Path to an APMANUAL file')
    args, rest = parser.parse_known_args()

    colorama.init()
    asyncio.run(main(args))
    colorama.deinit()

if __name__ == '__main__':
    launch()

# Pokemon TCG Ages Manual
Pokemon TCG: Ages is a custom "game" that stemmed from a desire to experience card interactions and deckbuilding across different eras of the Pokemon Trading Card Game that hadn't been played or existed together. There are custom formats that allow deckbuilding across all eras, but they frequently focus on the most overpowered cards from each era. Instead, I wanted this custom game to encourage interactions between game mechanics and evolution lines/powers that would lead to some creative deckbuilding.

The custom game centers around solitaire-style deck simulation, in that you'll build decks from the cards you've unlocked and your opponents will be static enemies for each "level". 

The game itself is built using an Archipelago apworld that was created with Manual for Archipelago, and operates as a randomized playthrough. For more information on Archipelago, go to [archipelago.gg](https://archipelago.gg/) or [join their Discord](https://discord.gg/archipelago). For more information on Manual for Archipelago, [join our Discord](https://discord.gg/T5bcsVHByx).

This game's apworld also demonstrates how you might want to use hooks in Manual. For more on that, see the heading below about hooks in Manual.

## Rules
- First turn rules follow Black and White era rules (no restrictions). Specifically:
  - The coin flip to see who goes first happens before drawing your starting hand and setting out your prizes.
    - If the opponent wins the coin flip, they automatically go first. If you win the coin flip, you choose whether you want to go first or second.
  - You draw a card to start your first turn as normal.
  - You can play a Supporter and any other card on your first turn, except Pokemon evolutions. Pokemon evolution rules are unchanged.
  - You can attack on your first turn.
- During setup, the opponent only places down the minimum number of static enemies required to make taking 6 prizes possible. 
  - e.g., if your enemy is an EX / other 2-prize Pokemon, you only set down the active and 2 benched to total 6 prizes. For the normal 1-prize Pokemon, set down the active + 5 benched.
- The opponent plays no other cards for the rest of the game, but does draw to start their turn.
- When the opponent takes a prize, that prize card is discarded.
- The opponent takes no actions during the game, except attacking and promoting a new attacker if their attacker is knocked out.
- The opponent can't attack on their first turn, but attacks every turn after.
  - They always prioritize attacks that take knockouts first, then attacks that do the maximum damage, in that order.
  - The opponent always has the required energy attached for their most expensive attack, even if the attack they use would discard that energy.
  - When any attacks are affected by the number of energy attached to the opponent, the opponent always has a number of energy attached equal to the cost of their most expensive attack.
  - When the opponent uses an attack with any negative side-effects for the opponent, the side-effects are negated entirely. 
    - If you're unsure, when in doubt, negate the secondary effect.
- If the opponent takes all 6 of their prizes or you can't draw a card to start your turn, you lose.
- If you take all 6 of your prizes or the opponent can't draw a card to start their turn, you win.

## Installing the Manual apworld
Grab the .apworld file from this repo's releases and put it in the `custom_worlds` folder of your Archipelago install.

You open the Manual PokemonTCGAges Client from the AP Launcher in your Archipelago install.

## Playing a Match
You use the simulator at https://ptcgsim.online/ to play. _(There's a Dark Mode setting on the Settings page, unless you're a degenerate that enjoys Light Mode.)_

**To set up a match:**
- Go the Import tab. Your deck will go in the "Main" tab, and the enemy's deck will go in the "Alt (1P Only)" tab.
- In the Manual PokemonTCGAges Client, make sure you're connected to the multiworld and click the "Deck Builder" tab (the blue one).
- Build your deck in the client above using the cards you've unlocked, the evolutions you have available, and basic energies.
- Use the "Export to Clipboard" button above your decklist in the client.
- Paste the copied decklist into the "Main" tab in the Import tab of the ptcgsim website, as mentioned above. Click the Import button, then click the Confirm button.
- Back in the Manual PTCGA Client, in the Deck Builder tab, choose the enemy (in the dropdown) based on whichever HP is listed for the location you're doing next.
- Click the "Copy Decklist" button in the client to copy your enemy's decklist.
- Paste the copied enemy decklist into the "Alt (1P Only)" tab in the Import tab of the ptcgsim website, as mentioned above. Click the Import button, then click the Confirm button.
- Go from the Import tab to the 1P tab on ptcgsim, and click the "Set Up Both" button at the bottom.
- Every time you take your turn, click the "+Turn" button to start your turn and have it draw a card for you.

## Can I Add More Cards to the Game?
Yes! This apworld includes a `test` pack that demonstrates how to add another "expansion pack" of cards. To add another pack like the `test` one, just create a directory in data and name it whatever the pack name should be (no spaces, no funny characters), and make sure you add an entry to the `pack_list.csv` file in data for your new pack.

By default, all packs are excluded except for the default one. There's a YAML option to include packs.

**Essentially, every pack of cards (including the default pack) has the following:**
- `card_list.csv` = A list of the cards you can receive / find
- `evolutions_list.csv` = A list of the evolutions that you need for the cards you can receive / find
- `energy_list.csv` = A list of basic energy cards (shouldn't be necessary to fill in for anything except default)
- `enemies.csv` = A list of enemies that you can potentially face

## Okay, but I want to learn about hooks in Manual
Check out [this document](hooks.md) that tells you all about how you might use hooks, and how they're used in this apworld!

## Wait, you're using a custom Manual client?!
That's right! This Manual apworld demonstrates how to have your own custom client that extends the existing Manual client. I use it to add a tab with custom functionality, among other things.

Check out [hooks/\_\_init\_\_.py](manual_pokemontcgages_fuzzy/hooks/__init__.py) to see how to register a custom client, and [hooks/client.py](manual_pokemontcgages_fuzzy/hooks/client.py) to see the custom client itself.

## I have some feedback or ideas to improve this
Awesome! [Join the Manual for Archipelago Discord](https://discord.gg/T5bcsVHByx) and post in the "Pokemon TCG: Ages" forum post in the "board-card-games" forum.

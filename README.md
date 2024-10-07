# Pokemon TCG: Ages (Manual)
**Legal bit:** Pokemon TCG: Ages is the name of a randomizer that uses a subset of Pokemon cards as a custom format to play the Pokemon TCG with. It is not a game, and is not endorsed by or affiliated with the Pokemon Company and related copyright holders.

Pokemon TCG: Ages is a randomizer that stemmed from a desire to experience card interactions and deckbuilding across different eras of the Pokemon Trading Card Game that hadn't been played or existed together. There are custom formats that allow deckbuilding across all eras, but they frequently focus on the most overpowered cards from each era. Instead, I wanted this more balanced (and randomized) format to encourage interactions between game mechanics and evolution lines/powers that would lead to some creative deckbuilding.

Playing the randomizer requires solitaire-style deck simulation, in that you'll build decks from the cards you've unlocked and your opponents will be static enemies for each "level". 

The randomizer itself is built using an Archipelago apworld that was created with Manual for Archipelago, and operates much like the randomized playthrough of any game. For more information on Archipelago, go to [archipelago.gg](https://archipelago.gg/) or [join their Discord](https://discord.gg/archipelago). For more information on Manual for Archipelago, [join our Discord](https://discord.gg/T5bcsVHByx).

This randomizer's apworld also demonstrates how you might want to use hooks in Manual. For more on that, see the heading below about hooks in Manual.

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
All you need to play is a way to play with the Pokemon cards that end up in your deck. That can be using physical cards, or making proxies, or some other way to simulate playing the Pokemon TCG. This randomizer is not specifically built for any of those methods, so that choice is up to you, the player!

**To pick a match to play:**
- In the Manual PokemonTCGAges Client, make sure you're connected to the multiworld and click the "Manual" tab.
- Pick the HP you'd like to face in an opponent, and expand that.
- Locations that say "Trial #" are just basic win-and-done matches. Beat the opponent, and you can check that location off!
- Locations that include the word "Challenge" will list what the challenge is. Play the match while obeying that challenge and, when you beat the opponent, check that location off!

**To set up a match:**
- In the Manual PokemonTCGAges Client, make sure you're connected to the multiworld and click the "Deck Builder" tab (the blue one).
- Build your deck in the client above using the cards you've unlocked, the evolutions you have available, and basic energies.
- Use the "Export to Clipboard" button above your decklist in the client to get your complete decklist.
- Use any of the methods above in "Playing a Match" to build your deck from the copied decklist in the previous step.
- Back in the Manual PTCGA Client, in the Deck Builder tab, choose the enemy (in the dropdown) based on whichever HP is listed for the location you're doing next.
- If you need a decklist for the enemy, you can get one by clicking "Copy Decklist".
- If you just need to see the enemy for the purpose of referencing their HP, abilities/powers/etc., and attacks, click the "View Card" button.
  - Since the enemy's deck is just 60 copies of itself, if you're playing with physical cards, I'd recommend just referencing the card instead of building the enemy deck.
- That's it! Once you have your deck and your enemy squared away, complete the battle (including any challenge it might have).

## Can I Add More Cards to this Randomizer?
Yes! This apworld includes a `test` pack that demonstrates how to add another "expansion pack" of cards. To add another pack like the `test` one, just create a directory in data and name it whatever the pack name should be (no spaces, no funny characters), and make sure you add an entry to the `pack_list.csv` file in data for your new pack.

By default, all packs are excluded except for the default one. There's a YAML option to include packs.

**Essentially, every pack of cards (including the default pack) has the following:**
- `card_list.csv` = A list of the cards you can receive / find
- `evolutions_list.csv` = A list of the evolutions that you need for the cards you can receive / find
- `energy_list.csv` = A list of basic energy cards (shouldn't be necessary to fill in for anything except default)
- `enemies.csv` = A list of enemies that you can potentially face

## Can I Ban Cards from this Randomizer?
Yep! There's a YAML option for that. You just list out whatever cards you want banned, like:
```
banned_cards:
   - Junk Arm TM 87
   - Mewtwo EX NXD 54
```
You can't ban the pre-evolution cards provided, and you can't ban any of the basic energy cards. Only cards you can receive as an item.

## Okay, but I want to learn about hooks in Manual
Check out [this document](hooks.md) that tells you all about how you might use hooks, and how they're used in this apworld!

## Wait, you're using a custom Manual client?!
That's right! This Manual apworld demonstrates how to have your own custom client that extends the existing Manual client. I use it to add a tab with custom functionality, among other things.

Check out [hooks/\_\_init\_\_.py](manual_pokemontcgages_fuzzy/hooks/__init__.py) to see how to register a custom client, and [hooks/client.py](manual_pokemontcgages_fuzzy/hooks/client.py) to see the custom client itself.

## I have some feedback or ideas to improve this
Awesome! [Join the Manual for Archipelago Discord](https://discord.gg/T5bcsVHByx) and post in the "Pokemon TCG: Ages" forum post in the "board-card-games" forum.

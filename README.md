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
  - You can play a Supporter and any other card on your first turn. Pokemon evolution rules are unchanged.
  - You can attack on your first turn.
- During setup, the opponent only places down the minimum number of static enemies required to make taking 6 prizes possible. 
- The opponent plays no other cards for the rest of the game.
- The opponent takes no actions during the game, except attacking, taking prizes, and promoting a new attacker if their attacker is knocked out.
- The opponent always attacks after their first turn.
  - Their static creatures always use the attack that does maximum damage, unless another attack guarantees a knockout, in which case they use that attack.
  - When the opponent uses an attack with any side-effects, the side-effects are negated entirely. When in doubt, negate the secondary effect.
  - When any attacks are amplified by the number of energy attached to the opponent, the opponent always has a number of energy attached equal to the most powerful attack they have to have energy attached for.

## Playing a Match
Nothing yet.

## Adding Custom Packs
Nothing yet.

## Okay, but I want to learn about hooks in Manual
Check out [this document](hooks.md) that tells you all about how you might use hooks, and how they're used in this apworld!

## Wait, you're using a custom Manual client?!
That's right! This Manual apworld demonstrates how to have your own custom client that extends the existing Manual client. I use it to add a tab with custom functionality, among other things.

Check out [hooks/\_\_init\_\_.py](manual_pokemontcgages_fuzzy/hooks/__init__.py) to see how to register a custom client, and [hooks/client.py](manual_pokemontcgages_fuzzy/hooks/client.py) to see the custom client itself.

## I have some feedback or ideas to improve this
Awesome! [Join the Manual for Archipelago Discord](https://discord.gg/T5bcsVHByx) and post in the "Pokemon TCG: Ages" forum post in the "board-card-games" forum.

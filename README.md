# diceutils
A Discord bot for rolling dice and doing math.

## Command Usage

This bot can evaluate mathematical expressions, which may or may not include dice rolls.

Specifically, the bot can perform operations on numbers (including decimal points, but not commas), and what I will call Dice Roll Expressions (or just dice rolls for short). 

It, however, does not support entering negative numbers in the expression (such as `-5`) at this time. To use a negative number, enter 0 minus the number (for example, to enter `-5`, use `(0-5)`). I may fix this limitation in the future, though it is not currently considered a critical issue.

The bot supports addition (`+`), subtraction (`-`), multiplication (`*`), division (`/`), and exponentiation (`^`).

### Dice Rolls

The bot also allows for dice rolls as terms in a mathematical expression. The syntax of a dice roll is as follows:

`[optional prefixed operation]<number of dice>d<number of sides>`

Examples include: `3d20` (roll 3 20-sided dice), and `adv2d8` (roll 2 8-sided dice with advantage (see next section)). Specifying a single die with syntax like `d20` is not currently supported, use `1d20` or similar.

#### Dice Operations

As the dice roll is treated as a single term in an expression, some operation must be performed to aggregate the rolls into one number. 

The supported operations are as follows:

* Sum (`sum`): This just sums the rolls. When no operation is specified, "sum" is assumed, though it can be specified explicitly as well.

* Disadvantage (`dis`): This returns the minimum of the rolls.

* Advantage (`adv`): This returns the maximum of the rolls.

* Average (`avg`): This returns the mean of the rolls.


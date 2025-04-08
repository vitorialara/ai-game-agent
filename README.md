# Colosseum Survival!

**Artifical Intelligence Project**  
Implemented by: Vitoria Lara Soria

## 🧠 Project Overview

Colosseum Survival is a two-player grid-based strategy game where agents must move across the board, place barriers, and control territory. The objective is to isolate your opponent and maximize your controlled area once the board is completely divided.

As part of the final project, I implemented a custom intelligent agent using **Monte Carlo Control** to learn and simulate optimal strategies for movement and wall placement.

---

## 🎯 Objectives

- Implement a custom agent that outperforms random baselines.
- Use reinforcement learning techniques to make intelligent decisions.
- Optimize territory control using simulations and episodic rollouts.
- Adapt the strategy based on changing board states and opponent behavior.

---

## 🧠 My Agent: `StudentAgent`

My custom agent (`StudentAgent`) uses a **Monte Carlo reinforcement learning strategy** to simulate many possible outcomes and select the best action.

### 🔍 How it works:

1. **Valid Action Generation**  
   It checks all possible movements and wall placements using a breadth-first search.

2. **Episode Simulation**  
   For each possible move, the agent simulates the rest of the game using a copied board state and checks the result with a Union-Find based endgame evaluator.

3. **Monte Carlo Evaluation**  
   It collects the outcome (score difference) for each simulated move and uses the average as the estimated value for that action.

4. **Move Selection**  
   The agent selects the move with the highest expected value. Immediate wins are chosen on the spot. Ties are stored as backups. Losses are discarded.

5. **Timeout Fail-safe**  
   A timer ensures decisions are made within the 2-second game tick constraint.

This strategy does not require a model of the environment and works purely from episodic simulation—a hallmark of Monte Carlo methods.

---

## Setup

To setup the game, clone this repository and install the dependencies:

```bash
pip install -r requirements.txt
```

## Playing a game

To start playing a game, we need to implement [_agents_](agents/agent.py). For example, to play the game using two random agents (agents which take a random action), run the following:

```bash
python simulator.py --player_1 random_agent --player_2 random_agent
```

This will spawn a random game board of size NxN, and run the two agents of class [RandomAgent](agents/random_agent.py). You will be able to see their moves in the console.

## Visualizing a game

To visualize the moves within a game, use the `--display` flag. You can set the delay (in seconds) using `--display_delay` argument to better visualize the steps the agents take to win a game.

```bash
python simulator.py --player_1 random_agent --player_2 random_agent --display
```

## Play on your own!

To play the game on your own, use a [`human_agent`](agents/human_agent.py) to play the game.

```bash
python simulator.py --player_1 human_agent --player_2 random_agent --display
```

## Autoplaying multiple games

Since boards are drawn randomly (between a [`MIN_BOARD_SIZE`](world.py#L17) and [`MAX_BOARD_SIZE`](world.py#L18)) you can compute an aggregate win % over your agents. Use the `--autoplay` flag to run $n$ games sequentially, where $n$ can be set using `--autoplay_runs`.

```bash
python simulator.py --player_1 random_agent --player_2 random_agent --autoplay
```

During autoplay, boards are drawn randomly between size `--board_size_min` and `--board_size_max` for each iteration.

**Notes**

- Not all agents supports autoplay. The variable `self.autoplay` in [Agent](agents/agent.py) can be set to `True` to allow the agent to be autoplayed. Typically this flag is set to false for a `human_agent`.
- UI display will be disabled in an autoplay.

## Full API

```bash
python simulator.py -h       
usage: simulator.py [-h] [--player_1 PLAYER_1] [--player_2 PLAYER_2]
                    [--board_size BOARD_SIZE] [--display]
                    [--display_delay DISPLAY_DELAY]

optional arguments:
  -h, --help            show this help message and exit
  --player_1 PLAYER_1
  --player_2 PLAYER_2
  --board_size BOARD_SIZE
  --display
  --display_delay DISPLAY_DELAY
  --autoplay
  --autoplay_runs AUTOPLAY_RUNS
```


## Game Rules

<p align="center">
  <img src="Gameboard.png" width="600" height="600">
</p>

### Game Setting
On an *M* x *M* chess board, 2 players are randomly distributed on the board with one player occupying one block.

### Game Moving
In each iteration, one player moves at most `K` steps (between `0` and `K`) in either horizontal or vertical direction, and must put a barrier around him or her in one of the 4 directions except the boarders of the chess board. The players move in a round-robin way.

#### Note: 
 - Each player cannot go into other player's place or put barriers in areas that already have barriers.
 - Currently the maximal number of steps is set to `K = (M + 1) // 2`.

### Game Ending
The game ends when each player is separated in a closed zone by the barriers and boundaries. The final score for each player will be the number of blocks in that zone.
```math
S_i = \#\text{Blocks of Zone}_i
```

### Goal
Each player should maximize the final score of itself, i.e., the number of blocks in its zone in the endgame.

### Example Gameplay
Here we show a gameplay describing a $`2`$-player game on a $`5\times 5`$ chessboard. Each player can move at most $`3`$ steps in each round.

<p align="center">
  <img src="Gameplay.gif" width="600" height="600">
</p>

The final score is $`A:B = 15:10`$. So A wins the game.

## Issues? Bugs? Questions?

Feel free to open an issue in this repository.


## License

[MIT](LICENSE)


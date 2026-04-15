# Othello AI Bot

A Python-based Othello game AI project featuring multiple agents, including 
a random player, Minimax, and Monte Carlo Tree Search (MCTS).

## Features
- Othello game implementation in Python
- Random AI agent
- Minimax AI agent
- MCTS AI agent
- GUI/game runner support

## Files
- `mcts_ai.py` – Monte Carlo Tree Search player
- `minimax_ai.py` – Minimax-based player
- `randy_ai.py` – Random baseline player
- `othello_game.py` – Game runner / main logic
- `othello_gui.py` – GUI support
- `othello_shared.py` – Shared helper functions and board logic

## How to Run
Run games from the terminal using the following commands:

### Random vs Random
```bash
py othello_game.py randy_ai.py randy_ai.py
```

### Minimax vs Random
```bash
py othello_game.py minimax_ai.py randy_ai.py
```

### MCTS vs Random
```bash
py othello_game.py mcts_ai.py randy_ai.py
```

### MCTS vs Minimax
```bash
py othello_game.py mcts_ai.py minimax_ai.py
```

### GUI Version
```bash
py othello_gui.py
```

## Notes
This project was built as part of an AI-focused academic assignment and 
explores different approaches to decision-making in turn-based games.

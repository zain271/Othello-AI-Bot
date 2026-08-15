# Othello AI Bot

A Python-based implementation of Othello/Reversi featuring multiple AI agents with different decision-making strategies, including Random, Minimax, and Monte Carlo Tree Search (MCTS).

## Features

- Randomized baseline AI
- Minimax AI with heuristic board evaluation
- Monte Carlo Tree Search (MCTS)
- UCT-based move selection
- Player vs AI mode
- AI vs AI mode
- Graphical user interface for gameplay

## AI Agents

### Random Agent
Selects from available legal moves randomly and serves as a baseline for comparing stronger agents.

### Minimax Agent
Uses the Minimax algorithm to explore future game states and select moves based on heuristic board evaluation.

### MCTS Agent
Uses Monte Carlo Tree Search to simulate possible outcomes before selecting a move. UCT is used to balance exploration of new moves with exploitation of promising moves.

## Technologies

- Python
- Minimax
- Monte Carlo Tree Search
- UCT
- Heuristic Evaluation

## Project Structure

- `othello_game.py` – core game logic
- `othello_gui.py` – graphical interface
- `othello_shared.py` – shared game functionality
- `randy_ai.py` – randomized AI agent
- `minimax_ai.py` – Minimax agent
- `mcts_ai.py` – MCTS agent

## Running the Project

Clone the repository and run:

```bash
python othello_gui.py

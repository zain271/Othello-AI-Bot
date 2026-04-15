# Othello AI Bot

A Python-based Othello game AI project featuring multiple agents, including a random player, Minimax, and Monte Carlo Tree Search (MCTS).

## Features
- Othello game implementation in Python
- Random AI agent
- Minimax AI agent
- MCTS AI agent
- GUI/game runner support

## ----- How to Run ------
Run games from the terminal using the following commands:
py othello_gui.py -d 8 -a randy_ai.py              ### YOU vs Random AI
py othello_gui.py -d 8 -a minimax_ai.py            ### YOU vs Minimax AI
py othello_gui.py -d 8 -a mcts_ai.py -l 1000 -h    ### YOU vs MCTS AI
py othello_gui.py -d 8 -a randy_ai.py -b randy_ai.py            ### Random AI vs Random AI
py othello_gui.py -d 8 -a mcts_ai.py -b randy_ai.py -l 1000     ### MCTS AI vs Random AI
py othello_gui.py -d 8 -a mcts_ai.py -b minimax_ai.py -l 1000   ### MCTS AI vs Minimax AI

## Notes
This project was built as part of an AI-focused academic assignment and 
explores different approaches to decision-making in turn-based games.

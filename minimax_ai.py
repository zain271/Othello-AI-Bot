#!/usr/bin/env python3
# -*- coding: utf-8 -*
"""
Minimax is a "AI" for Othello that chooses a legal move using the Minimax
algorithm. Play against this AI if you want an opponent who is more competetive
than randy. You can also have your AI compete
against your AI to test its performance.
"""

# You can also use any function in othello_shared to write your AI
from othello_shared import eprint, get_possible_moves, get_score, play_move

NODE_COUNT = 0 #global counter, to count nodes generated
ROOT_COLOR = 0 #global to store root color

class MinimaxNode:
    def __init__(self, board, color, move, parent=None, depth=0, max_depth=6):
        self.board = board
        self.color = color
        self.move = move
        self.parent = parent
        self.children = []
        self.depth = depth              # Current depth in the tree
        self.max_depth = max_depth      # Maximum depth allowed
        self.value = None

    def is_terminal(self):
        """
        Check if the game is over or if depth limit is reached.
        """
        return len(get_possible_moves(self.board,self.color)) == 0 or self.depth >= self.max_depth

    def evaluate(self):
        """
        Evaluate the game state for terminal or depth-limited nodes.
        """
        global ROOT_COLOR
        score = get_score(self.board)
        if ROOT_COLOR == 1: return score[0] - score[1]
        else: return score[1] - score[0]

    def expand(self):
        """
        Generate child nodes for all legal moves.
        """
        opponent = 1
        if self.color == 1: opponent = 2

        legal_moves = get_possible_moves(self.board, self.color)

        for move in legal_moves:
            next_board = play_move(self.board, self.color, move[0], move[1])
            child_node = MinimaxNode(
                board=next_board,
                color=opponent,
                move=move,
                parent=self,
                depth=self.depth + 1,
                max_depth=self.max_depth
            )
            global NODE_COUNT
            NODE_COUNT = NODE_COUNT + 1 #log a node expansion
            self.children.append(child_node)

    def minimax(self):
        """
        Perform minimax search up to the depth limit.
        """
        global ROOT_COLOR
        if self.is_terminal():
            self.value = self.evaluate()
            return self.value

        self.expand()

        if self.color == ROOT_COLOR:
            self.value = max(child.minimax() for child in self.children)
        else:
            self.value = min(child.minimax() for child in self.children)

        return self.value

    def best_child(self):
        """
        After minimax, choose the best move based on evaluation.
        """
        global ROOT_COLOR
        if not self.children:
            return None

        if self.color == ROOT_COLOR:
            return max(self.children, key=lambda c: c.value)
        else:
            return min(self.children, key=lambda c: c.value)

def select_move_minimax(board, color):
    """
               You can add additional help functions as long as this function will return a position tuple
    """
    global NODE_COUNT, ROOT_COLOR
    NODE_COUNT = 0
    ROOT_COLOR = color
    initial_state = MinimaxNode(board, color, None, 0, 0,6)
    NODE_COUNT = NODE_COUNT + 1 #log a node expansion
    initial_state.minimax()
    return initial_state.best_child().move


def run_ai():
    """
    This function establishes communication with the game manager.
    It first introduces itself and receives its color.
    Then it repeatedly receives the current score and current board state
    until the game is over.
    """
    print("Minimax")  # First line is the name of this AI

    arguments = input().split(",")
    color = int(arguments[0])  # We read the color: 1 for dark (goes first), 2 for light.

    # Arguments below have no impact on Minimax but will impact your AI.
    limit = int(arguments[1])
    heuristic = bool(int(arguments[2]))

    while True:  # This is the main loop
        # Read in the current game status, for example:
        # "SCORE 2 2" or "FINAL 33 31" if the game is over.
        # The first number is the score for player 1 (dark), the second for player 2 (light)
        next_input = input()
        status, dark_score_s, light_score_s = next_input.strip().split()

        if status == "FINAL":  # Game is over.
            print("-1 -1")
        else:
            board = eval(input())  # Read in the input and turn it into a Python
            # object. The format is a list of rows. The
            # squares in each row are represented by
            # 0 : empty square
            # 1 : dark disk (player 1)
            # 2 : light disk (player 2)

            # Select the move and send it to the manager
            movei, movej = select_move_minimax(board, color)
            print("{} {}".format(movei, movej))


if __name__ == "__main__":
    run_ai()

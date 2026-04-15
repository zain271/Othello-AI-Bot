"""
An AI player for Othello.
"""
# You can use the functions in othello_shared to write your AI
import math
import random
import numpy as np

from othello_shared import get_possible_moves, get_score, play_move, eprint

NODE_COUNT = 0 #global counter, to count nodes generated

def heuristic_fn(state):
    """
    Write your heuristic, and doctests for your heuristic, here
    """
    """
    Heuristic function for evaluating Othello board states.

    The heuristic estimates how favorable a board position is for the current player.
    It combines three key factors commonly used in Othello strategy:

    1. Corner Control:
       Corners are extremely valuable because pieces placed there cannot be flipped.
       We reward states where the player controls more corners than the opponent.

    2. Mobility:
       The number of legal moves available to each player.
       A higher number of moves gives more flexibility and control over the game.
       We prefer states where the player has more available moves than the opponent.

    3. Disk Difference:
       The difference in the number of pieces on the board.
       While less important early in the game, it still provides a useful signal.

    The final heuristic value is a weighted sum of these components:
        heuristic = (corner_score * 25) + (mobility_score * 5) + disk_difference

    A higher value indicates a better position for the current player.

    Input:
        state = (board, color)

    Output:
        A numeric score representing the desirability of the state.
    """
    board, color = state
    opponent = 2 if color == 1 else 1
    n = len(board)

    #corner control
    corners = [(0, 0), (0, n - 1), (n - 1, 0), (n - 1, n - 1)]
    my_corners = 0
    opp_corners = 0
    for x, y in corners:
        if board[y][x] == color:
            my_corners += 1
        elif board[y][x] == opponent:
            opp_corners += 1
    corner_score = 25 * (my_corners - opp_corners)

    #mobility
    my_moves = len(get_possible_moves(board, color))
    opp_moves = len(get_possible_moves(board, opponent))
    mobility_score = 5 * (my_moves - opp_moves)

    #disk difference
    p1, p2 = get_score(board)
    if color == 1:
        disk_score = p1 - p2
    else:
        disk_score = p2 - p1

    return corner_score + mobility_score + disk_score

class MCTSNode:

    def __init__(self, parent, children, reward, total, board, color, move, root_color):
        self.board = board # board at this state
        self.color = color # color at this state
        self.move = move #move that got us to this state
        self.parent = parent  # parent state
        self.children = children  # child states
        self.reward = reward  # number of wins at this state
        self.total = total  # number of simulations anchored at this state
        self.colour_at_root = root_color

    def get_children(self):
        return self.children

    def get_move(self):
        return self.move

    def get_total(self):
        return self.total

    def ucb_score(self) -> float:
        """
        Calculates the Upper Confidence Bound (UCB) score.
        >>> parent = MCTSNode(None, None, 0, 10, None, None, None, None)
        >>> child = MCTSNode(parent, None, 5, 5, None, None, None, None)
        >>> round(child.ucb_score(), 4)
        1.9597
        >>> parent = MCTSNode(None, None, 0, 20, None, None, None, None)
        >>> child = MCTSNode(parent, None, 10, 10, None, None, None, None)
        >>> round(child.ucb_score(), 4)
        1.774
        >>> parent = MCTSNode(None, None, 0, 100, None, None, None, None)
        >>> child = MCTSNode(parent, None, 0, 0, None, None, None, None)
        >>> child.ucb_score()
        inf
        """
        if self.total == 0:
            return float("inf")

        exploitation = self.reward / self.total

        if self.parent is None or self.parent.total == 0:
            exploration = 0
        else:
            exploration = math.sqrt(2 * math.log(self.parent.total) / self.total)

        return exploitation + exploration

    def best_ucb_node(self):
        """
        Returns the child node with the highest UCB score.
        However, if any child has not been visited (i.e., total == 0),
        it should be returned immediately (it's UCB score is Infinite)
        >>> parent = MCTSNode(None, None, 0, 10, None, 1, None,1)
        >>> child1 = MCTSNode(parent, None, 3, 3, None, 2, None,1)
        >>> child2 = MCTSNode(parent, None, 0, 0, None, 2, None,1)
        >>> child3 = MCTSNode(parent, None, 6, 6, None, 2, None,1)
        >>> parent.children = [child1, child2, child3]
        >>> best = parent.best_ucb_node()
        >>> best is child2
        True
        >>> parent = MCTSNode(None, None, 0, 20, None, 1, None, 1)
        >>> child1 = MCTSNode(parent, None, 10, 5, None, 2, None, 1)
        >>> child2 = MCTSNode(parent, None, 5, 10, None, 2, None, 1)
        >>> parent.children = [child1, child2]
        >>> best = parent.best_ucb_node()
        >>> best is child1  # best, if root player is player 1
        True
        >>> parent = MCTSNode(None, None, 0, 20, None, 1, None,2)
        >>> child1 = MCTSNode(parent, None, 10, 5, None, 2, None,2)
        >>> child2 = MCTSNode(parent, None, 5, 10, None, 2, None,2)
        >>> parent.children = [child1, child2]
        >>> best = parent.best_ucb_node()
        >>> best is child2  # best, if root player is player 2
        True
        """
        if not self.children:
            return None

        for child in self.children:
            if child.total == 0:
                return child

        if self.color == self.colour_at_root:
            return max(self.children, key=lambda c: c.ucb_score())
        else:
            return min(self.children, key=lambda c: c.ucb_score())

    def best_move(self):
        """
        Returns the move corresponding to the child of
        the given node that has been visited (sampled) the most.
        >>> child1 = MCTSNode(None, None, 0, 5, None, None, "A", None)
        >>> child2 = MCTSNode(None, None, 0, 10, None, None, "B", None)
        >>> child3 = MCTSNode(None, None, 0, 3, None, None, "C", None)
        >>> p = MCTSNode(None, None, 0, 0, None, None, None, None)
        >>> p.children = [child1, child2, child3]
        >>> p.best_move()
        'B'
        >>> child1 = MCTSNode(None, None, 0, 10, None, None, "A", None)
        >>> child2 = MCTSNode(None, None, 0, 10, None, None, "B", None)
        >>> child3 = MCTSNode(None, None, 0, 5, None, None, "C", None)
        >>> p = MCTSNode(None, None, 0, 0, None, None, None, None)
        >>> p.children = [child1, child2, child3]
        >>> p.best_move() in ["A", "B"]
        True
        """
        if not self.children:
            return None
        best_child = max(self.children, key=lambda c: c.total)
        return best_child.move

    def simulate(self, heuristic = False):
        """
        Runs a simulation (playout) from the current board state until the end of the game.
        Chooses moves randomly unless `heuristic=True`, in which case a heuristic function
        selects the next move.

        After the simulation finishes, the result is back-propagated.

        Args:
            heuristic (bool): Whether to use a heuristic function instead of random move selection.

        Returns:
            None

        >>> board = ((0, 2, 0, 0, 0, 0), (0, 2, 1, 0, 1, 0), (0, 1, 1, 1, 1, 0), (0, 0, 0, 0, 1, 0), (0, 0, 0, 0, 1, 0), (0, 0, 0, 0, 1, 0))
        >>> child = MCTSNode(None, [], 0, 10, board, 1, None, 1)
        >>> node = MCTSNode(None, [child], 0, 10, board, 1, None, 1)
        >>> child.parent = node
        >>> child.simulate()
        >>> child.total
        11
        >>> child.simulate()
        >>> child.total
        12
        >>> node.total
        12
        """
        current_board = self.board
        current_color = self.color

        while True:
            moves = get_possible_moves(current_board, current_color)

            #game should end immediately if player has no legal moves left.
            if not moves:
                break

            if heuristic:
                best_val = -float("inf")
                best_moves = []

                for move in moves:
                    next_board = play_move(current_board, current_color, move[0], move[1])
                    val = heuristic_fn((next_board, current_color))

                    if val > best_val:
                        best_val = val
                        best_moves = [move]
                    elif val == best_val:
                        best_moves.append(move)

                move = random.choice(best_moves)
            else:
                move = random.choice(moves)

            current_board = play_move(current_board, current_color, move[0], move[1])
            current_color = 2 if current_color == 1 else 1

        p1, p2 = get_score(current_board)
        if self.colour_at_root == 1:
            win = p1 > p2
        else:
            win = p2 > p1

        self.back_propagate(win)

    def back_propagate(self, win: bool):
        """
        Recursively backpropagates the result of a simulation up the tree.
        Increments visit count (`total`) for each node in the path, and
        increments reward if the simulation resulted in a win.

        Args:
            win (bool): True if the simulation resulted in a win for the root player,
                        False otherwise.

        >>> root = MCTSNode(None, [], 0, 0, None, 1, None, 1)
        >>> child = MCTSNode(root, [], 0, 0, None, 2, None, 1)
        >>> root.children.append(child)
        >>> child.back_propagate(True)
        >>> root.total
        1
        >>> root.reward
        1
        >>> child.total
        1
        >>> child.reward
        1
        """
        self.total += 1
        if win:
            self.reward += 1

        if self.parent is not None:
            self.parent.back_propagate(win)

    def select(self):
        """
        Descends tree using UCB scores until a leaf node is reached.

        Returns:
            MCTSNode: A leaf node (no children).

        >>> root = MCTSNode(None, [], 0, 10, None, 1, None, 1)
        >>> child1 = MCTSNode(root, [], 5, 5, None, 1, 'A', 1)
        >>> child2 = MCTSNode(root, [], 10, 10, None, 1, 'B', 1)
        >>> grandchild1 = MCTSNode(child1, [], 8, 8, None, 1, 'B1', 1)
        >>> grandchild2 = MCTSNode(child1, [], 6, 6, None, 1, 'B2', 1)
        >>> root.children = [child1, child2]
        >>> child1.children = [grandchild1, grandchild2]
        >>> leaf = root.select()
        >>> leaf is grandchild2
        True
        >>> leaf.select() is leaf
        True
        """
        current = self
        while current.children:
            current = current.best_ucb_node()
        return current

    def expand(self):
        """
        Expands a node by generating all valid child nodes.

        Returns:
            MCTSNode: One of the newly created child nodes, or None if terminal.

        >>> board = ((0, 2, 0, 0, 0, 0), (0, 2, 1, 0, 1, 0), (0, 1, 1, 1, 1, 0), (0, 0, 0, 0, 1, 0), (0, 0, 0, 0, 1, 0), (0, 0, 0, 0, 1, 0))
        >>> root = MCTSNode(None, [], 0, 0, board, 1, None, 1)
        >>> child = root.expand()
        >>> len(root.children) > 0
        True
        >>> child in root.children
        True
        """
        global NODE_COUNT

        moves = get_possible_moves(self.board, self.color)
        if not moves:
            return None

        opponent = 2 if self.color == 1 else 1

        for move in moves:
            next_board = play_move(self.board, self.color, move[0], move[1])
            child_node = MCTSNode(
                parent=self,
                children=[],
                reward=0,
                total=0,
                board=next_board,
                color=opponent,
                move=move,
                root_color=self.colour_at_root
            )
            self.children.append(child_node)
            NODE_COUNT += 1

        return random.choice(self.children)

    def mcts_step(self, heuristic = False):
        """" Run an MCTS iteration.

        Args:
            heuristic (bool): allow for heuristic guided simulations,
            as opposed to random simulations, if heuristic is true.
        """
        cur = self.select() #select a leaf node
        if cur.total > 0: cur = cur.expand() #if it has been simulated, expand it and select a child
        if cur is not None:
            cur.simulate(heuristic) #simulate a game play from the selected node

def select_move_mcts(board, color, iters = 10000, heuristic = False):
    """
    Selects the best move for a given board and color using Monte Carlo Tree Search (MCTS).

    Initializes an MCTS root node, runs the MCTS search for a fixed number
    of iterations (`iters`), and then selects the best move found during the search.

    Args:
        board (list of lists): The current board state.
        color (int): The player's color (1 or 2).
        iters (int): The number of MCTS iterations to perform.

    Returns:
        tuple: The move (i, j) chosen as the best move after MCTS.
    """
    global NODE_COUNT
    NODE_COUNT = 0
    initial_state = MCTSNode(None, [], 0, 0, board, color, None, color)
    NODE_COUNT += 1 #made the first node!
    initial_state.expand() #expand the first node to set things up

    #do our MCTS iterations
    for itr in range(iters):
        initial_state.mcts_step(heuristic)

    #pick the best move so far
    return initial_state.best_move()

####################################################
def run_ai():
    """
    This function establishes communication with the game manager.
    It first introduces itself and receives its color.
    Then it repeatedly receives the current score and current board state
    until the game is over.
    """
    print("Monte Carlo AI")   #name given by me is Monte Carlo AI
    arguments = input().split(",")

    color = int(arguments[0]) #Player color: 1 for dark (goes first), 2 for light.
    iterations = int(arguments[1])  #limit on iterations
    heuristic = bool(int(arguments[2]))  #heuristic to be used or not?
    if iterations == -1: iterations = 1000

    eprint(f'Iterations {iterations} heuristic {heuristic}')

    while True: #this is the main loop
        #Read in the current game status, for example:
        #"SCORE 2 2" or "FINAL 33 31" if the game is over.
        #the first number is the score for player 1 (dark), the second for player 2 (light)
        next_input = input()
        status, dark_score_s, light_score_s = next_input.strip().split()

        if status == "FINAL": #game is over.
            print("-1 -1")
        else:
            board = eval(input()) #read in the input and turn it into a Python
                                  #object. The format is a list of rows. The
                                  #squares in each row are represented by
                                  #0 : empty square
                                  #1 : dark disk (player 1)
                                  #2 : light disk (player 2)

            #select the move and send it to the manager
            movei, movej = select_move_mcts(board, color, iterations, heuristic)

            print("{} {}".format(movei, movej))

if __name__ == "__main__":
    #import doctest
    #doctest.testmod()
    run_ai()



#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module contains the main Othello game which maintains the board, score, and 
players.  

Thanks to original author Daniel Bauer, Columbia University
"""
import sys
import signal
import subprocess
import time
from threading import Timer

WRITE_TO_FILE = True

from othello_shared import eprint, find_lines, get_possible_moves, play_move, get_score

class InvalidMoveError(RuntimeError):
    pass

class AiTimeoutError(RuntimeError):
    pass


class Player(object):
    def __init__(self, color, name="Human"):
        self.name = name
        self.color = color

    def get_move(self, manager):
        pass  

class AiPlayerInterface(Player):

    TIMEOUT = 10

    def __init__(self, filename, color, limit, heuristic = 0):

        self.color = color
        self.time = 0
        try:           #---------IMPORTANT NOTE: changed "python3" to "py" here----------------
            self.process = subprocess.Popen(['py',filename], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            name = self.process.stdout.readline().decode("ASCII").strip()
            print("AI introduced itself as: {}".format(name))
            self.name = name
            try:
                # Only write if stdin is open
                if self.process.stdin:
                    self.process.stdin.write(
                        (str(color) + "," + str(limit) + "," + str(heuristic) + "," + str(limit) + "," + str(heuristic) + "\n").encode("ASCII"))
                    self.process.stdin.flush()
            except (BrokenPipeError, IOError):
                print('BrokenPipeError caught', file=sys.stderr)

        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def timeout(self):
        sys.stderr.write("{} timed out. ".format(self.name))
        elapsed = time.perf_counter() - self.time
        sys.stderr.write(f"Timer fired after {elapsed:.2f} seconds")
        if WRITE_TO_FILE:
            with open("solutions/result.txt", "a") as f:
                f.write("\n{} timed out!!".format(self.name))
        try:
            if self.process.stdin:
                self.process.stdin.close()
        except (BrokenPipeError, IOError):
            pass
        self.process.kill()
        self.timed_out = True

    def get_move(self, manager):
        white_score, dark_score = get_score(manager.board)
        print((white_score, dark_score))
        try:
            # Only write if stdin is still open
            if self.process.stdin:
                self.process.stdin.write("SCORE {} {}\n".format(white_score, dark_score).encode("ASCII"))
                self.process.stdin.flush()
                self.process.stdin.write("{}\n".format(str(manager.board)).encode("ASCII"))
                self.process.stdin.flush()
        except (BrokenPipeError, IOError):
            print('BrokenPipeError caught', file=sys.stderr)

        self.time = time.perf_counter()
        timer = Timer(AiPlayerInterface.TIMEOUT, lambda: self.timeout())
        self.timed_out = False
        timer.start()
        i,j = -1,-1

        # Wait for the AI call
        try:
            # Only read if stdout is open
            if self.process.stdout:
                move_s = self.process.stdout.readline().decode("ASCII")
                if self.timed_out:
                    raise AiTimeoutError
                timer.cancel()
                i_s, j_s = move_s.strip().split()
                i = int(i_s)
                j = int(j_s)
        except (BrokenPipeError, IOError):
            print('BrokenPipeError caught', file=sys.stderr)

        return i,j

    def kill(self, manager):
        white_score, dark_score = get_score(manager.board)
        try:
            if self.process.stdin and not self.process.stdin.closed:
                self.process.stdin.write("FINAL {} {}\n".format(white_score, dark_score).encode("ASCII"))
                self.process.stdin.flush()
                self.process.stdin.close()
        except (BrokenPipeError, IOError):
            pass  # Process may already be dead
        try:
            if self.process.stdout and not self.process.stdout.closed:
                self.process.stdout.close()
        except (BrokenPipeError, IOError):
            pass
        if self.process.poll() is None:  # Only kill if still running
            self.process.kill()
        self.process.wait()

class OthelloGameManager(object):

    def __init__(self, dimension = 6):

        self.dimension = dimension
        self.board = self.create_initial_board()
        self.current_player = 1
        self.players = []
            
    def create_initial_board(self):
        board = []
        for i in range(self.dimension): 
            row = []
            for j in range(self.dimension):
                row.append(0)
            board.append(row) 

        i = self.dimension // 2 -1
        j = self.dimension // 2 -1
        board[i][j] = 2
        board[i+1][j+1] = 2
        board[i+1][j] = 1
        board[i][j+1] = 1
        final = []
        for row in board: 
            final.append(tuple(row))
        return board

    def print_board(self):
        for row in self.board: 
            print(" ".join([str(x) for x in row]))
                   
    def play(self, i,j):
        if self.board[j][i] != 0:
           raise InvalidMoveError("Occupied square.")
        lines = find_lines(self.board, i,j, self.current_player)
        if not lines:  
           raise InvalidMoveError("Invalid Move.")
     
        self.board = play_move(self.board, self.current_player, i, j) 
        self.current_player = 1 if self.current_player == 2 else 2

    def get_possible_moves(self):
        return get_possible_moves(self.board, self.current_player)

def play_game(game, player1, player2):
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    players = [None, player1, player2]

    while True: 
        player_obj = players[game.current_player]
        possible_moves = game.get_possible_moves() 
        if not possible_moves: 
            p1score, p2score = get_score(game.board)
            print("FINAL: {} (dark) {}:{} {} (light)".format(player1.name, p1score, p2score, player2.name))
            player1.kill(game)
            player2.kill(game)
            break 
        else: 
            color = "dark" if game.current_player == 1 else "light"
            try: 
                i, j = player_obj.get_move(game)
                print("{} ({}) plays {},{}".format(player_obj.name, color, i,j))
                eprint("{} ({}) plays {},{}".format(player_obj.name, color, i, j))
                game.play(i,j)
            except AiTimeoutError:
                p1score, p2score = get_score(game.board)  # Get score here
                print("{} ({}) timed out!".format(player_obj.name, color))
                print("FINAL: {} (dark) {}:{} {} (light)".format(player1.name, p1score, p2score, player2.name))
                player1.kill(game)
                player2.kill(game)
                break



#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module contains a simple graphical user interface for Othello. 

Thanks to original author Daniel Bauer, Columbia University
"""
import sys, getopt

from tkinter import *
from tkinter import scrolledtext

from othello_game import OthelloGameManager, AiPlayerInterface, Player, InvalidMoveError, AiTimeoutError
from othello_shared import eprint, get_possible_moves, get_score

WRITE_TO_FILE = False

class OthelloGui(object):

    def __init__(self, game_manager, player1, player2):

        self.game = game_manager
        self.players = [None, player1, player2]
        self.height = self.game.dimension
        self.width = self.game.dimension 
        
        self.offset = 3
        self.cell_size = 50

        root = Tk()
        root.wm_title("Othello")
        root.lift()
        root.attributes("-topmost", True)
        self.root = root
        self.canvas = Canvas(root,height = self.cell_size * self.height + self.offset,width = self.cell_size * self.width + self.offset)
        self.move_label = Label(root)
        self.score_label = Label(root)
        self.text = scrolledtext.ScrolledText(root, width=70, height=10)
        self.move_label.pack(side="top")
        self.score_label.pack(side="top")
        self.canvas.pack()
        self.text.pack()
        self.draw_board()

    def get_position(self,x,y):
        i = (x -self.offset) // self.cell_size
        j = (y -self.offset) // self.cell_size
        return i,j

    def mouse_pressed(self,event):
        i,j = self.get_position(event.x, event.y)

        try:
            player = "Dark" if self.game.current_player == 1 else "Light"
            self.log("{}: {},{}".format(player, i, j))
            self.game.play(i, j)
            self.draw_board()
            if not get_possible_moves(self.game.board, self.game.current_player):
                self.shutdown(f"Game Over: {self.game.current_player} played an impossible move.")
                eprint("\nFinal Score: " + self.score_label["text"])
                if WRITE_TO_FILE:
                    with open("result.txt", "a") as f:
                        f.write("\nFinal Score: " + self.score_label["text"])
                self.root.after(1000, self.root.destroy)
                sys.exit(1)
            elif isinstance(self.players[self.game.current_player], AiPlayerInterface):
                self.root.unbind("<Button-1>")
                self.root.after(100,lambda: self.ai_move())
        except InvalidMoveError:
            self.log("Invalid move. {},{}".format(i,j))

    def shutdown(self, text):
        self.move_label["text"] = text 
        self.root.unbind("<Button-1>")
        if isinstance(self.players[1], AiPlayerInterface): 
            self.players[1].kill(self.game)
        if isinstance(self.players[2], AiPlayerInterface): 
            self.players[2].kill(self.game)
 
    def ai_move(self):
        player_obj = self.players[self.game.current_player]
        try:
            i,j = player_obj.get_move(self.game)
            player = "Dark" if self.game.current_player == 1 else "Light"
            player = "{} {}".format(player_obj.name, player)
            self.log("{}: {},{}".format(player, i,j))
            self.game.play(i,j)
            self.draw_board()
            self.root.update()
            if not get_possible_moves(self.game.board, self.game.current_player):
                self.shutdown("Game Over")
                eprint("\nFinal Score: " + self.score_label["text"])
                if WRITE_TO_FILE:
                    with open("result.txt", "a") as f:
                        f.write("\nFinal Score: " + self.score_label["text"])
                self.root.after(100, self.root.destroy)
                sys.exit(1)
            elif isinstance(self.players[self.game.current_player], AiPlayerInterface):
                self.root.after(1, lambda: self.ai_move())
            else: 
                self.root.bind("<Button-1>",lambda e: self.mouse_pressed(e))        
        except AiTimeoutError:
            self.shutdown("Game Over, {} lost (timeout)".format(player_obj.name))
            if WRITE_TO_FILE:
                with open("result.txt", "a") as f:
                    f.write("\nFinal Score: " + self.score_label["text"])
            eprint("\nFinal Score: " + self.score_label["text"])
            self.root.after(100, self.root.destroy)
            sys.exit(1)

    def run(self):
        try:
            if isinstance(self.players[1], AiPlayerInterface):
                self.root.after(10, lambda: self.ai_move())
            else:
                self.root.bind("<Button-1>",lambda e: self.mouse_pressed(e))
        except (BrokenPipeError, IOError):
            print("Error encountered.")

        self.draw_board()
        self.canvas.mainloop()

    def draw_board(self):
        self.draw_grid()
        self.draw_disks()
        player = "Dark" if self.game.current_player == 1 else "Light"
        if len(self.game.players) > 0:
            player = self.game.players[self.game.current_player].name

        self.move_label["text"]= player
        self.score_label["text"]= "Dark {} : {} Light".format(*get_score(self.game.board)) 
   
    def log(self, msg, newline = True): 
        self.text.insert("end","{}{}".format(msg, "\n" if newline else ""))
        self.text.see("end")
 
    def draw_grid(self):
        for i in range(self.height):
            for j in range(self.width):
                self.canvas.create_rectangle(i*self.cell_size + self.offset, j*self.cell_size + self.offset, (i+1)*self.cell_size + self.offset, (j+1)*self.cell_size + self.offset, fill="dark green")
       
    def draw_disk(self, i,j, color):
        x = i * self.cell_size + self.offset
        y = j * self.cell_size + self.offset
        padding = 2
        self.canvas.create_oval(x+padding, y+padding, x+self.cell_size-padding, y+self.cell_size-padding, fill=color)
        
    def draw_disks(self):
        for i in range(self.height): 
            for j  in range(self.width): 
                if self.game.board[i][j] == 1:
                    self.draw_disk(j, i, "black")
                elif self.game.board[i][j] == 2:
                    self.draw_disk(j, i, "white")

def main(argv):

    size = 0
    iterations = -1
    heuristic = 0
    agent1 = None
    agent2 = None

    try:
        opts, args = getopt.getopt(argv,"hl:d:a:b:",["iterations=","dimension=","agent1=","agent2="])
    except getopt.GetoptError:
        print('othello_gui.py -d <dimension> -a <agentA> [-b <agentB> -l <iterations> -h]')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-d", "--dimension"):
            size = int(arg)
        elif opt in ("-a", "--agentA"):
            agent1 = arg
        elif opt in ("-b", "--agentB"):
            agent2 = arg    
        elif opt in ("-h", "--heuristic"):
            heuristic = 1
        elif opt in ("-l", "--iterations"):
            iterations = int(arg)
        else:
            print('othello_gui.py -d <dimension> -a <agentA> [-b <agentB> -l <iteration-iterations> -h]')
            sys.exit()

    if size <= 0: #if no dimension provided
        print('Please provide a board size.')
        print('othello_gui.py -d <dimension> [-a <agentA> -b <agentB> -l <iteration-iterations> -h]')
        sys.exit(2)  

    if agent1 is not None and agent2 is not None and size > 0:
        p1 = AiPlayerInterface(agent1,1,iterations,heuristic)
        p2 = AiPlayerInterface(agent2,2,iterations,heuristic)
    elif agent1 is not None and size > 0:
        p1 = Player(1)
        p2 = AiPlayerInterface(agent1,2,iterations,heuristic)
    else: 
        p1 = Player(1)
        p2 = Player(2)

    game = OthelloGameManager(size)
    gui = OthelloGui(game, p1, p2)
    gui.run()

if __name__ == "__main__":
    main(sys.argv[1:])

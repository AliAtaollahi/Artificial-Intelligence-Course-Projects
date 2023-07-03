# from select import select
# from symbol import dotted_as_name
import turtle
import math
import random
import time
from time import sleep
from sys import argv
from dataclasses import dataclass
import copy


END_GAME_VAL = 1000

@dataclass
class State:
    red : list
    blue : list
    available_moves : list

class take_stop_watch:
    def __init__(self):
        pass
    
    def __enter__(self):
        self.start = time.time()
    
    def __exit__(self, *args):
        self.end = time.time()
        print(f'executed in {(self.end-self.start):.3f} sec')
        print()

class Sim:
    # Set true for graphical interface
    GUI = False
    screen = None
    selection = []
    turn = ''
    dots = []
    red = []
    blue = []
    available_moves = []
    minimax_depth = 0
    prune = False

    def __init__(self, minimax_depth, prune, gui):
        self.GUI = gui
        self.prune = prune
        self.minimax_depth = minimax_depth
        if self.GUI:
            self.setup_screen()
        self.nodes_meeted = 0

    def setup_screen(self):
        self.screen = turtle.Screen()
        self.screen.setup(800, 800)
        self.screen.title("Game of SIM")
        self.screen.setworldcoordinates(-1.5, -1.5, 1.5, 1.5)
        self.screen.tracer(0, 0)
        turtle.hideturtle()

    def draw_dot(self, x, y, color):
        turtle.up()
        turtle.goto(x, y)
        turtle.color(color)
        turtle.dot(15)

    def gen_dots(self):
        r = []
        for angle in range(0, 360, 60):
            r.append((math.cos(math.radians(angle)), math.sin(math.radians(angle))))
        return r

    def initialize(self):
        self.selection = []
        self.available_moves = []
        for i in range(0, 6):
            for j in range(i, 6):
                if i != j:
                    self.available_moves.append((i, j))
        if random.randint(0, 2) == 1:
            self.turn = 'red'
        else:
            self.turn = 'blue'
        self.dots = self.gen_dots()
        self.red = []
        self.blue = []
        if self.GUI: turtle.clear()
        self.draw()

    def draw_line(self, p1, p2, color):
        turtle.up()
        turtle.pensize(3)
        turtle.goto(p1)
        turtle.down()
        turtle.color(color)
        turtle.goto(p2)

    def draw_board(self):
        for i in range(len(self.dots)):
            if i in self.selection:
                self.draw_dot(self.dots[i][0], self.dots[i][1], self.turn)
            else:
                self.draw_dot(self.dots[i][0], self.dots[i][1], 'dark gray')

    def draw(self):
        if not self.GUI: return 0
        self.draw_board()
        for i in range(len(self.red)):
            self.draw_line((math.cos(math.radians(self.red[i][0] * 60)), math.sin(math.radians(self.red[i][0] * 60))),
                           (math.cos(math.radians(self.red[i][1] * 60)), math.sin(math.radians(self.red[i][1] * 60))),
                           'red')
        for i in range(len(self.blue)):
            self.draw_line((math.cos(math.radians(self.blue[i][0] * 60)), math.sin(math.radians(self.blue[i][0] * 60))),
                           (math.cos(math.radians(self.blue[i][1] * 60)), math.sin(math.radians(self.blue[i][1] * 60))),
                           'blue')
        self.screen.update()
        sleep(1)
    
                
    def is_not_triangle(self, nodes, i, j):
        for p in range(len(nodes)):
            for q in range(p+1,len(nodes)):
                if nodes[p][1] == nodes[q][1] or nodes[p][1] == nodes[q][0] or nodes[p][0] == nodes[q][0] :
                    points = set([nodes[p][0], nodes[p][1], nodes[q][0], nodes[q][1]])
                    if i in points and j in points:
                        return False
        return True     

    def _evaluate(self, state):
        red_triangle = 0
        blue_triangle = 0
        state.red.sort()
        state.blue.sort()
        for (i,j) in state.available_moves:
            red_triangle += self.is_not_triangle(state.red, i, j)
            blue_triangle += self.is_not_triangle(state.blue, i, j)
            
        return -END_GAME_VAL if red_triangle == 0 else \
                END_GAME_VAL if blue_triangle == 0 else \
                red_triangle - blue_triangle

    def minimax(self, depth, player_turn, state):    
        if depth == self.minimax_depth:
            return self._evaluate(state)
        value = 0
        final_move = 0
        ########################################################################################################## 
        if player_turn == 'red': # max
            value = - math.inf
            state.red.sort()

            for i in range (len(state.available_moves)):
                self.nodes_meeted += 1
                move = state.available_moves[i]
                if self.is_not_triangle(state.red, move[0], move[1]) == 0:
                    if value < -END_GAME_VAL:
                        value = -END_GAME_VAL
                        final_move = move
                    continue
            
                available_moves_copy = copy.deepcopy(state.available_moves)
                available_moves_copy.pop(i)
                state.red.append(move)
                result_value = self.minimax(depth + 1, 'blue', State(state.red, state.blue, available_moves_copy))
                state.red.remove(move)
                if result_value >= value:
                    value = result_value
                    final_move = move
        ##########################################################################################################
        elif player_turn == 'blue' :  # min
            value = math.inf
            state.blue.sort()

            for i in range(len(state.available_moves)):
                self.nodes_meeted += 1
                move = state.available_moves[i]
                if self.is_not_triangle(state.blue, move[0], move[1]) == 0:
                    if value > END_GAME_VAL:
                        value = END_GAME_VAL
                        final_move = move
                    continue
                
                available_moves_copy = copy.deepcopy(state.available_moves)
                available_moves_copy.pop(i)
                state.blue.append(move)
                result_value = self.minimax(depth + 1, 'red', State(state.red, state.blue, available_moves_copy))
                state.blue.remove(move)
                if result_value < value:
                    value = result_value
                    final_move = move
        ##########################################################################################################
        if  depth == 0:
          return final_move
        return value
    
    def minimax_with_prune(self, depth, player_turn, state, alpha=-math.inf, beta=math.inf):
        if depth == self.minimax_depth:
            return self._evaluate(state)
        value = 0
        final_move = 0
        ##########################################################################################################
        if player_turn == 'red':  # max
            value = - math.inf
            state.red.sort()

            for i in range (len(state.available_moves)):
                self.nodes_meeted += 1
                move = state.available_moves[i]
                if self.is_not_triangle(state.red, move[0], move[1]) == 0:
                    if value < -END_GAME_VAL:
                        value = -END_GAME_VAL
                        final_move = move
                        if value >= beta :
                            break
                        alpha = max(alpha, value)
                    continue
            
                available_moves_copy = copy.deepcopy(state.available_moves)
                available_moves_copy.pop(i)
                state.red.append(move)
                result_value = self.minimax_with_prune(depth + 1, 'blue', State(state.red, state.blue, available_moves_copy), alpha, beta)
                state.red.remove(move)
                if result_value >= value:
                    value = result_value
                    final_move = move
                    if value >= beta :
                        break
                    alpha = max(alpha, result_value)
        ##########################################################################################################
        elif player_turn == 'blue' :  # min
            value = math.inf
            state.blue.sort()

            for i in range(len(state.available_moves)):
                self.nodes_meeted += 1
                move = state.available_moves[i]
                if self.is_not_triangle(state.blue, move[0], move[1]) == 0:
                    if value > END_GAME_VAL:
                        value = END_GAME_VAL
                        final_move = move
                        if value <= alpha :
                            break
                        beta = min(beta, value)
                    continue
                
                available_moves_copy = copy.deepcopy(state.available_moves)
                available_moves_copy.pop(i)
                state.blue.append(move)
                result_value = self.minimax_with_prune(depth + 1, 'red', State(state.red, state.blue, available_moves_copy), alpha, beta)
                state.blue.remove(move)
                if result_value < value:
                    value = result_value
                    final_move = move
                    if value <= alpha :
                        break
                    beta = min(beta, value)
        ##########################################################################################################
        if  depth == 0:
          return final_move
        return value
    
    def enemy(self):
        return random.choice(self.available_moves)
    
    def play(self):
        self.initialize()
        selection = []
        while True:
            if self.turn == 'red':
                if self.prune:
                    selection = self.minimax_with_prune(0, player_turn=self.turn,
                                         state=State(self.red, self.blue, self.available_moves))
                else:
                    selection = self.minimax(0, player_turn=self.turn,
                                         state=State(self.red, self.blue, self.available_moves))
                if selection[1] < selection[0]:
                    selection = (selection[1], selection[0])
            else:
                selection = self.enemy()
                if selection[1] < selection[0]:
                    selection = (selection[1], selection[0])
            if selection in self.red or selection in self.blue:
                raise Exception("Duplicate Move!!!")
            if self.turn == 'red':
                self.red.append(selection)
            else:
                self.blue.append(selection)

            self.available_moves.remove(selection)
            self.turn = self._swap_turn(self.turn)
            selection = []
            self.draw()
            r = self.gameover(self.red, self.blue)
            if r != 0:
                return r
    
    def _swap_turn(self, turn):
        if turn == 'red':
            return 'blue'
        else:
            return 'red'
            
    def gameover(self, r, b):
        if len(r) < 3 and len(b) < 3:
            return 0
        r.sort()
        for i in range(len(r) - 2):
            for j in range(i + 1, len(r) - 1):
                for k in range(j + 1, len(r)):
                    if r[i][0] == r[j][0] and r[i][1] == r[k][0] and r[j][1] == r[k][1]:
                        return 'blue'
        if len(b) < 3: return 0
        b.sort()
        for i in range(len(b) - 2):
            for j in range(i + 1, len(b) - 1):
                for k in range(j + 1, len(b)):
                    if b[i][0] == b[j][0] and b[i][1] == b[k][0] and b[j][1] == b[k][1]:
                        return 'red'
        return 0

if __name__=="__main__":
    number_of_tests = 100
    game = Sim(minimax_depth=int(argv[1]), prune=False, gui=bool(int(argv[2])))
    with take_stop_watch():
        results = {"red": 0, "blue": 0}
        for i in range(number_of_tests):
            results[game.play()] += 1
        
        print(results)
        print('avg nodes meeted :', game.nodes_meeted / number_of_tests)
    
#!/usr/bin/env python
#-*- coding: utf-8 -*-

from itertools import cycle
from math import *
from operator import itemgetter
from copy import deepcopy
#from draw import *

import pygame, sys, random, copy, time
    
# the configuration
rows = (8, 9)
cell_size = 100
delay= 750
white = (255, 255, 255)

colors = [
(255, 0,   0  ),
(0,   150, 0  ),
(0,   0,   255),
(255, 120, 0  ),
(255, 255, 0  ),
(180, 0,   255),
(0,   220, 220)
]
                
class Hexic():
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(250, 25)
        self.height = cell_size*9
        self.width = cell_size*10
        self.position = [[4 ,3], [5, 3], [5, 4]]
        self.count = 1
        self.count_pair = [1, 0]
        self.extra = -1
        self.rotating = True
        self.circle_parts = 0
        
        self.key_actions = {
            'ESCAPE':   sys.exit,
            'LEFT':     self.move_left,
            'RIGHT':    self.move_right,
            'DOWN':     self.move_down,
            'UP':       self.move_up,
            'q':        self.rotate_counterclockwise,
            'e':        self.rotate_clockwise,
        }
        
        self.moves = [  'DOWN',
                        'UP',
                        'LEFT',
                        'RIGHT'  ]

        #pygame.event.set_blocked(pygame.MOUSEMOTION) # we do not need mouse movement events, so we block them.
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.board = [[random.choice(colors) for j in range(rows[i%2])] for i in range(10)]
        self.find_clusters()
    
    def draw_hexagon(self, color, radius, position): # draws hexagon
        pygame.draw.polygon(self.screen, color, [(position[0] + radius * cos(2 * pi * i / 6), position[1] + radius * sin(2 * pi * i / 6))for i in range(6)])
        
    def draw_matrix(self, board):
        for x, column in enumerate(board):
            off_x = cell_size/2
            off_y = off_x * abs(x%2-2)
            for y, color in enumerate(column):
                position = (off_x+(x*cell_size), self.height-(off_y+(y*cell_size)))
                self.draw_hexagon(color, off_x, position)
                if [x, y] in self.position or (x, y) in self.clusters:
                    self.draw_hexagon(white, cell_size/4, position)
        pygame.display.update()
                
    def find_clusters(self):
        self.clusters = set([])
        for x, column in enumerate(self.board):
            previous_color = None
            for y, current_color in enumerate(column):
                if current_color == previous_color:
                    temp_circle_parts = 2
                    if x < 8 and y < 8:
                        temp_circle_parts += [self.board[x+2][y], self.board[x+2][y-1], self.board[x+1][y-(1+(x%2))], self.board[x+1][y+(1-(x%2))]].count(current_color)
                        self.circle_parts += temp_circle_parts
                        #print (temp_circle_parts, self.circle_parts)
                        if temp_circle_parts == 6:
                            if self.board[x+1][y-(x%2)] == white:
                                self.extra = x
                            self.clusters = set([(x, y), (x, y-1), (x+2, y-1), (x+2, y), (x+1, y-(1+(x%2))), (x+1, y+(1-(x%2)))])
                            self.board[x+1][y-(x%2)] = white

                            break
                    if x > 0:
                        if self.board[x-1][y-x%2] == current_color: # might be incorrect
                            self.clusters.add((x, y))
                            self.clusters.add((x, y-1))
                            self.clusters.add((x-1, y-x%2))
                    if x < 9:
                        if self.board[x+1][y-x%2] == current_color: # might be incorrect
                            self.clusters.add((x, y))
                            self.clusters.add((x, y-1))
                            self.clusters.add((x+1, y-x%2))
                previous_color = current_color
        if len(self.clusters) > 0:
            self.rotating = False
            self.draw_matrix(self.board)
            time.sleep(0.5)
            self.remove_clusters()
            self.find_clusters()
    
    def remove_clusters(self):
        coordinates_list = list(self.clusters)
        x, y = coordinates_list[0]
        coordinates_list.sort(key=itemgetter(0, 1), reverse=True)
        for coordinate_pair in coordinates_list:
            del self.board[coordinate_pair[0]][coordinate_pair[1]]
            if self.extra != -1:
                self.board[x].append(white)
                self.extra = -1
            else:
                self.board[coordinate_pair[0]].append(random.choice(colors))
        
    def move_left(self):
        x, y = self.position[0]
        if len(self.position) == 3 and self.board[x][y] == (255, 255, 255) and x != self.position[1][0]:
            self.temp_position = self.position
            self.position = [[x-1, y], [x-1, y+1-2*(x%2)], [x+1, y], [x+1, y+1-2*(x%2)], [x, y-1], [x, y+1]]
        elif len(self.position) == 3:
            self.position[1][0]-=self.count*2
            self.position[2][0]-=2
        else:
            self.position = [self.position[0], self.position[1], [self.position[3][0], self.position[3][1]-1]]
            self.count = 1
            
    def move_right(self):
        x, y = self.position[2]
        if len(self.position) == 3 and self.board[x][y] == (255, 255, 255) and x != self.position[1][0]:
            self.temp_position = self.position
            self.position = [[x-1, y], [x-1, y+1-2*(x%2)], [x+1, y], [x+1, y+1-2*(x%2)], [x, y-1], [x, y+1]]
        elif len(self.position) == 3:
            self.position[1][0]+=2-(2*self.count)
            self.position[0][0]+=2
        else:
            self.position = [[self.position[3][0], self.position[3][1]-1], self.position[4], self.position[5]]
            self.count = 0
    
    def move_up(self):
        if len(self.position) == 6:
            self.move_left()
        else:
            self.position[self.count][0]+=1-(self.count*2)
            self.position[self.count][1]+=1+(self.position[0][0]%2)

    def move_down(self):
        if len(self.position) == 6:
            self.move_left()
        else:
            self.position[self.count+1][0]+=1-(self.count*2)
            self.position[self.count+1][1]-=2-(self.position[2][0]%2)
    
    def rotate(self, direction):
        r = 3
        self.rotating = True
        if len(self.position) == 6:
            self.position = [self.position[0], self.position[1], self.position[3], self.position[5], self.position[4], self.position[2]]
            r = 1
        colors = [self.board[coordinate_pair[0]][coordinate_pair[1]] for coordinate_pair in self.position]
        if direction == "clockwise":
            if self.count == 1 and len(self.position) == 3:
                self.position = list(reversed(self.position))
                colors = list(reversed(colors))
        else:
            if self.count == 0 or len(self.position) == 6:
                self.position = list(reversed(self.position))
                colors = list(reversed(colors))
        for i in range(r): #len(colors)):
            time.sleep(0.1)
            for index, coordinate_pair in enumerate(self.position):
                if self.rotating:
                    self.board[coordinate_pair[0]][coordinate_pair[1]] = colors[index-i-1]
            self.find_clusters()
            self.draw_matrix(self.board) 
        
    def rotate_clockwise(self): # just do this three times
        self.rotate("clockwise")
        
    def rotate_counterclockwise(self):
        self.rotate("counterclockwise")
    
    def run(self):
        #pygame.time.set_timer(pygame.USEREVENT+1, delay)

        while True:
            self.draw_matrix(self.board)
            self.circle_parts = 0
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    for key in self.key_actions:
                        if event.key == eval("pygame.K_"+key):
                            temp_position = copy.deepcopy(self.position)
                            self.key_actions[key]()
                            for coordinate_pair in self.position:
                                if (any(-1 in coordinate_pair or 10 in coordinate_pair for coordinate_pair in self.position)) or coordinate_pair[1] >= len(self.board[coordinate_pair[0]%2]):
                                    self.position = temp_position
                            if key in self.moves and self.position != temp_position:
                                self.count = self.count_pair[self.count]
                    self.position.sort(key=itemgetter(0, 1))
                    if len(self.position) == 6 and (self.board[self.position[1][0]+1][self.position[1][1]-(self.position[1][0]%2)] != white):
                        self.position = self.temp_position
                        self.count = self.count_pair[self.count]
            #yield
                    # insert position assert (2 conditions)

            #pygame.time.Clock().tick(20)

#Hexic = Hexic()

if __name__ == '__main__':
   Hexic().run()

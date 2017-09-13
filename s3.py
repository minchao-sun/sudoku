#!/usr/bin/env python
# -*- coding:utf-8 -*-
#  
# Project: sudoku
# Author: Minchao Sun
# Created: 2017/9/8 10:08

from __future__ import print_function
import copy

try:
    import pygame
    from pygame.locals import *

    PYGAME = True
except ImportError:
    PYGAME = False


def main():
    data = "data1.txt"
    f = open(data, 'r')
    m = {}
    for iii in range(9):
        line = f.readline()
        s = line.split()
        for jjj in range(9):
            if s[jjj] != '0':
                m[(iii, jjj)] = int(s[jjj])
    f.close()

    sudoku = Sudoku(m)
    sudoku.check()

    if not sudoku.is_complete():
        sudoku.test()

    print("Error:", sudoku.check_error())
    print("Completed:", sudoku.is_complete())
    sudoku.draw_board()


class Sudoku:
    def __init__(self, num_map=None):
        if num_map is None:
            num_map = {}
        self.map = {}
        self.origin = num_map
        self.values = {}
        self.rows = []
        self.columns = []
        self.boxes = []
        self.solved = 0

        for i in range(9):
            self.rows.append(list(range(1, 10)))
            self.columns.append(list(range(1, 10)))
            self.boxes.append(list(range(1, 10)))
            for j in range(9):
                self.map[(i, j)] = ' '
                self.values[(i, j)] = list(range(1, 10))

        for pos in num_map:
            # fill num using given clues
            self.fill_num(pos, num_map[pos])

    def is_filled(self, pos):
        return self.map[pos] in range(1, 10)

    def is_empty(self, pos):
        return self.map[pos] not in range(1, 10)

    def is_complete(self):
        for pos in self.map:
            if self.is_empty(pos):
                return False
        return True

    def is_possible(self, pos, val):
        if self.is_filled(pos):
            return False
        else:
            return val in self.possible_value(pos)

    def display_console(self):
        for i in range(9):
            if i == 3 or i == 6:
                print("---------------------")
            for j in range(9):
                if j == 3 or j == 6:
                    print('|', end=' ')
                print(self.map[(i, j)], end=' ')
            print('')

    def draw_board(self):
        global PYGAME
        if not PYGAME:
            self.display_console()
            return
        pygame.init()
        text = pygame.font.Font("Century.TTF", 30)
        screen = pygame.display.set_mode((640, 480), 0, 32)
        screen.fill((235, 235, 235))
        point1 = []
        point2 = []
        for i in range(10):
            point1.append((40, 40 * i + 40))
            point1.append((400, 40 * i + 40))
            point2.append((40 * i + 40, 40))
            point2.append((40 * i + 40, 400))
        for i in range(0, len(point1), 2):
            if i % 3 == 0:
                pygame.draw.line(screen, (0, 0, 0), point1[i], point1[i + 1], 2)
                pygame.draw.line(screen, (0, 0, 0), point2[i], point2[i + 1], 2)
            else:
                pygame.draw.line(screen, (0, 0, 0), point1[i], point1[i + 1], 1)
                pygame.draw.line(screen, (0, 0, 0), point2[i], point2[i + 1], 1)

        num_blue = []
        num_black = []
        clue = 0
        for i in range(9):
            num_blue.append(text.render(str(i + 1), False, (0, 70, 255)))
            num_black.append(text.render(str(i + 1), False, (20, 20, 20)))
        for pos in self.map:
            if self.is_empty(pos):
                continue
            if pos in self.origin:
                clue += 1
                screen.blit(num_black[self.map[pos] - 1], (52 + 40 * pos[1], 42 + 40 * pos[0]))
            else:
                screen.blit(num_blue[self.map[pos] - 1], (52 + 40 * pos[1], 42 + 40 * pos[0]))
        clue_text = text.render("Clues: " + str(clue), False, (0, 0, 0))
        screen.blit(clue_text, (450, 60))

        # update the screen
        pygame.display.update()
        # waiting to exit
        while True:
            event = pygame.event.wait()
            if event.type == QUIT:
                exit(0)

    def fill_num(self, pos, num):
        # set value on that position
        self.map[pos] = num
        self.values[pos] = []
        # exclude the value
        self.exclude(pos, num)
        self.solved += 1

    def possible_value(self, pos):
        """get the possible value of this position"""
        if self.is_filled(pos):
            return []
        l1 = self.rows[pos[0]]
        l2 = self.columns[pos[1]]
        l3 = self.boxes[int(pos[0] / 3) * 3 + int(pos[1] / 3)]
        # get the common elements in the three lists
        l = [x for x in l1 if x in l2 and x in l3]
        l = [x for x in l if x in self.values[pos]]
        return l

    def exclude(self, pos, val):
        if val in self.rows[pos[0]]:
            self.rows[pos[0]].remove(val)
        if val in self.columns[pos[1]]:
            self.columns[pos[1]].remove(val)
        if val in self.boxes[int(pos[0] / 3) * 3 + int(pos[1] / 3)]:
            self.boxes[int(pos[0] / 3) * 3 + int(pos[1] / 3)].remove(val)

    def check(self):
        for pos in self.map:
            if self.is_filled(pos):
                continue
            # get the possible value list
            self.values[pos] = self.possible_value(pos)
            # if there is only one possible value
            if len(self.values[pos]) == 1:
                # fill the number
                self.fill_num(pos, self.values[pos][0])
                self.check()
                return

        for i in range(9):
            for val in self.rows[i]:
                count = 0
                for j in range(9):
                    if self.is_possible((i, j), val):
                        count += 1
                if count == 1:
                    for j in range(9):
                        if self.is_possible((i, j), val):
                            self.fill_num((i, j), val)
                            self.check()
                            return

            for val in self.columns[i]:
                count = 0
                for j in range(9):
                    if self.is_possible((j, i), val):
                        count += 1
                if count == 1:
                    for j in range(9):
                        if self.is_possible((j, i), val):
                            self.fill_num((j, i), val)
                            self.check()
                            return

            for val in self.boxes[i]:
                count = 0
                for j in range(9):
                    p1 = int(i / 3) * 3 + int(j / 3)
                    p2 = int(i % 3) * 3 + int(j % 3)
                    if self.is_possible((p1, p2), val):
                        count += 1
                if count == 1:
                    for j in range(9):
                        p1 = int(i / 3) * 3 + int(j / 3)
                        p2 = int(i % 3) * 3 + int(j % 3)
                        if self.is_possible((p1, p2), val):
                            self.fill_num((p1, p2), val)
                            self.check()
                            return

    def check_error(self):
        for i in range(9):
            lst = list(self.rows[i])
            for j in range(9):
                pos = (i, j)
                if self.is_empty(pos) and len(self.values[pos]) == 0:
                    return True
                if self.is_filled(pos):
                    lst.append(self.map[pos])
            lst.sort()
            if lst != list(range(1, 10)):
                return True

            lst = list(self.columns[i])
            for j in range(9):
                pos = (j, i)
                if self.is_filled(pos):
                    lst.append(self.map[pos])
            lst.sort()
            if lst != list(range(1, 10)):
                return True

            lst = list(self.boxes[i])
            for j in range(9):
                pos = (int(i / 3) * 3 + int(j / 3), int(i % 3) * 3 + int(j % 3))
                if self.is_filled(pos):
                    lst.append(self.map[pos])
            lst.sort()
            if lst != list(range(1, 10)):
                return True
        return False

    def test(self):
        # try some possible values
        for pos in self.map:
            if len(self.values[pos]) < 4:
                self.test2(pos)
        if self.is_complete():
            return
        # if not completed
        for pos in self.map:
            if self.is_empty(pos):
                self.test2(pos)
        if self.is_complete():
            return
        # if not completed
        for pos in self.map:
            if len(self.values[pos]) < 4:
                print("***** Deep test *****")
                self.deep_test(pos)

    def test2(self, pos):
        for val in self.values[pos]:
            tmp = copy.deepcopy(self)
            tmp.fill_num(pos, val)
            tmp.check()
            if tmp.check_error():
                print("Wrong", pos, val)
                if self.is_possible(pos, val):
                    self.values[pos].remove(val)
                self.check()
                return

    def deep_test(self, pos):
        for val in self.values[pos]:
            t1 = copy.deepcopy(self)
            t1.fill_num(pos, val)
            t1.check()
            if t1.check_error():
                print("Wrong", pos, val)
                if self.is_possible(pos, val):
                    self.values[pos].remove(val)
                self.check()
            else:
                for p in t1.map:
                    if len(t1.values[p]) > 3:
                        continue
                    t1.test2(p)
                if not t1.check_error() and t1.is_complete():
                    self.map = t1.map.copy()
                    self.values = t1.values.copy()
                    self.rows = list(t1.rows)
                    self.boxes = list(t1.boxes)
                    self.columns = list(t1.columns)
                    return


if __name__ == '__main__':
    main()

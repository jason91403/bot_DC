#!/usr/bin/env python
# -*- coding: utf-8 -*-


class GameDictionary(object):

    text_door = "+"
    can_pass_text_list = [".", "'", "(", ")", ">", "<", "†", "[", "$", "=", "!", "%", "?"]
    """
        '(', ')': something can be picked up (use ,key)
        '†': some monster died here before
        "'": open door
        '>': staircase
        '[': some armour
        '$': money
        '=': some ring
        '!': some items(can be used)
        '^': shaft
        '+': door
        '%': food
    """

    def __init__(self):
        pass

    def get_can_pass_text_list(self):
        return self.can_pass_text_list

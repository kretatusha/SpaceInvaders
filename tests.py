import os
import pickle
from unittest import TestCase, main

import pygame

import new_space_invaders
from new_space_invaders import Game
from menu.usertable import UserTable
from menu.userdata import UserData

class GameTest(TestCase):
    def test_level_count_on_start_without_safe(self):
        table = UserTable('data/table.txt')
        s = Game(table)
        self.assertEqual(s.level, 1)

    def test_level_count_on_start_with_safe(self):
        if os.path.exists('data/data.pickle'):
            with open('data/data.pickle', 'rb') as f:
                data = pickle.load(f)
        s = Game(current_level=data['current_level'])
        self.assertEqual(s.level, data['current_level'])

    def test_load_previous_game(self):
        table = UserTable('data/table.txt')
        s = Game(name='check')
        s.save_data()
        pygame.quit()
        if os.path.exists('data/data.pickle'):
            with open('data/data.pickle', 'rb') as f:
                data = pickle.load(f)
        s = Game(name = data['name'])
        self.assertEqual(s.name,'check')

    def test_check_res(self):
        if os.path.exists('data/table.txt'):
            os.remove('data/table.txt')
        table = UserTable('data/table.txt')
        s = Game(name='check',table = table)
        s.level = 2
        s.score =200
        s.save_results()
        pygame.quit()
        res = s.table
        self.assertEqual(f'{s.name},{s.score},{s.level}', res.table[0].to_string())



if __name__ == '__main__':
    main()

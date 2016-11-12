# coding: utf-8
from mikado import Goals
from unittest import TestCase


class GoalsTest(TestCase):
    def setUp(self):
        self.goals = Goals('Root')

    def test_there_is_one_goal_at_start(self):
        assert self.goals.all() == {1: 'Root'}
        assert self.goals.top() == {1: 'Root'}

    def test_new_goal_moves_to_top(self):
        self.goals.add('A')
        assert self.goals.all() == {1: 'Root', 2: 'A'}
        assert self.goals.top() == {2: 'A'}

    def test_two_new_goals_move_to_top(self):
        self.goals.add('A')
        self.goals.add('B')
        assert self.goals.all() == {1: 'Root', 2: 'A', 3: 'B'}
        assert self.goals.top() == {2: 'A', 3: 'B'}

    def test_two_goals_in_a_chain(self):
        self.goals.add('A')
        self.goals.add('AA', 2)
        assert self.goals.all() == {1: 'Root', 2: 'A', 3: 'AA'}
        assert self.goals.top() == {3: 'AA'}

    def test_rename_goal(self):
        self.goals.add('Boom')
        self.goals.rename(2, 'A')
        assert self.goals.all() == {1: 'Root', 2: 'A'}

    def test_insert_goal_in_the_middle(self):
        self.goals.add('B')
        self.goals.insert(1, 2, 'A')
        assert self.goals.all() == {1: 'Root', 2: 'B', 3: 'A'}
        assert self.goals.top() == {2: 'B'}

    def test_close_single_goal(self):
        assert self.goals.all(keys='name,open') == {
                1: {'name': 'Root', 'open': True}}
        self.goals.close(1)
        assert self.goals.all() == {1: 'Root'}
        assert self.goals.top() == {}
        assert self.goals.all(keys='name,open') == {
                1: {'name': 'Root', 'open': False}}

    def test_reopen_goal(self):
        self.goals.add('A')
        self.goals.close(2)
        assert self.goals.all(keys='open') == {1: True, 2: False}
        self.goals.reopen(2)
        assert self.goals.all(keys='open') == {1: True, 2: True}

    def test_delete_single_goal(self):
        self.goals.add('A')
        self.goals.delete(2)
        assert self.goals.all() == {1: 'Root'}

    def test_enumeration_could_be_changed_after_delete(self):
        self.goals.add('A')
        self.goals.add('B')
        assert self.goals.all() == {1: 'Root', 2: 'A', 3: 'B'}
        self.goals.delete(2)
        assert self.goals.all() == {1: 'Root', 2: 'B'}

    def test_remove_goal_chain(self):
        self.goals.add('A')
        self.goals.add('B', 2)
        self.goals.delete(2)
        assert self.goals.all() == {1: 'Root'}
from siebenapp.enumeration import Enumeration
from siebenapp.goaltree import Goals


def test_simple_enumeration_is_not_changed():
    goals = Goals('a')
    goals.add('b')
    goals.add('c')
    goals.select(2)
    goals.hold_select()
    goals.select(3)
    goals.toggle_link()
    e = Enumeration(goals)
    assert e.all(keys='name,edge') == {
        1: {'name': 'a', 'edge': [2, 3]},
        2: {'name': 'b', 'edge': [3]},
        3: {'name': 'c', 'edge': []},
    }


def test_apply_mapping_for_the_10th_element():
    goals = Goals('a')
    for i, c in enumerate('bcdefghij'):
        goals.add(c)
        goals.select(i + 2)
    e = Enumeration(goals)
    assert e.all(keys='name,edge') == {
        1: {'name': 'a', 'edge': [2]},
        2: {'name': 'b', 'edge': [3]},
        3: {'name': 'c', 'edge': [4]},
        4: {'name': 'd', 'edge': [5]},
        5: {'name': 'e', 'edge': [6]},
        6: {'name': 'f', 'edge': [7]},
        7: {'name': 'g', 'edge': [8]},
        8: {'name': 'h', 'edge': [9]},
        9: {'name': 'i', 'edge': [0]},
        0: {'name': 'j', 'edge': []},
    }
    # simulate goal addition
    goals.select(1)
    goals.add('k')
    assert e.all(keys='name,edge') == {
        11: {'name': 'a', 'edge': [12, 21]},
        12: {'name': 'b', 'edge': [13]},
        13: {'name': 'c', 'edge': [14]},
        14: {'name': 'd', 'edge': [15]},
        15: {'name': 'e', 'edge': [16]},
        16: {'name': 'f', 'edge': [17]},
        17: {'name': 'g', 'edge': [18]},
        18: {'name': 'h', 'edge': [19]},
        19: {'name': 'i', 'edge': [10]},
        10: {'name': 'j', 'edge': []},
        21: {'name': 'k', 'edge': []},
    }


def test_use_mapping_in_selection():
    goals = Goals('a')
    for i, c in enumerate('bcdefghij'):
        goals.add(c)
        goals.select(i + 2)
    e = Enumeration(goals)
    e.select(0)
    assert e.all(keys='name,select') == {
        1: {'name': 'a', 'select': 'prev'},
        2: {'name': 'b', 'select': None},
        3: {'name': 'c', 'select': None},
        4: {'name': 'd', 'select': None},
        5: {'name': 'e', 'select': None},
        6: {'name': 'f', 'select': None},
        7: {'name': 'g', 'select': None},
        8: {'name': 'h', 'select': None},
        9: {'name': 'i', 'select': None},
        0: {'name': 'j', 'select': 'select'},
    }
    e.add('k')
    e.select(1)
    e.select(6)
    assert e.all(keys='name,select') == {
        11: {'name': 'a', 'select': 'prev'},
        12: {'name': 'b', 'select': None},
        13: {'name': 'c', 'select': None},
        14: {'name': 'd', 'select': None},
        15: {'name': 'e', 'select': None},
        16: {'name': 'f', 'select': 'select'},
        17: {'name': 'g', 'select': None},
        18: {'name': 'h', 'select': None},
        19: {'name': 'i', 'select': None},
        10: {'name': 'j', 'select': None},
        21: {'name': 'k', 'select': None},
    }


def test_mapping_for_top():
    goals = Goals('a')
    goals.add('b')
    for i, c in enumerate('cdefghijklmnopqrstuv'):
        goals.add(c)
        goals.delete(i + 3)         # 1: a, 2: b, 3 (i==0): c, 4 (i==1): d, ...
    goals.add('x')
    e = Enumeration(goals)
    assert e.all(keys='name,top,select') == {
        1: {'name': 'a', 'top': False, 'select': 'select'},
        2: {'name': 'b', 'top': True, 'select': None},
        3: {'name': 'x', 'top': True, 'select': None},
    }


def test_toggle_switch_view():
    e = Enumeration(Goals('Root'))
    assert e.view == 'open'
    e.next_view()
    assert e.view == 'top'
    e.next_view()
    assert e.view == 'full'
    e.next_view()
    assert e.view == 'open'


def test_goaltree_selection_may_be_changed_in_top_view():
    goals = Goals('Root')
    goals.add('Top 1')
    goals.add('Top 2')
    e = Enumeration(goals)
    assert e.all(keys='name,top,select') == {
        1: {'name': 'Root', 'top': False, 'select': 'select'},
        2: {'name': 'Top 1', 'top': True, 'select': None},
        3: {'name': 'Top 2', 'top': True, 'select': None},
    }
    e.next_view()
    assert e.events[-2] == ('select', 2)
    assert e.events[-1] == ('hold_select', 2)
    assert e.all(keys='name,top,select') == {
        1: {'name': 'Top 1', 'top': True, 'select': 'select'},
        2: {'name': 'Top 2', 'top': True, 'select': None}
    }


def test_goaltree_previous_selection_may_be_changed_in_top_view():
    goals = Goals('Root')
    goals.add('Top 1')
    goals.add('Top 2')
    goals.hold_select()
    goals.select(2)
    e = Enumeration(goals)
    assert e.all(keys='name,top,select') == {
        1: {'name': 'Root', 'top': False, 'select': 'prev'},
        2: {'name': 'Top 1', 'top': True, 'select': 'select'},
        3: {'name': 'Top 2', 'top': True, 'select': None},
    }
    e.next_view()
    assert e.events[-1] == ('hold_select', 2)
    assert e.all(keys='name,top,select') == {
        1: {'name': 'Top 1', 'top': True, 'select': 'select'},
        2: {'name': 'Top 2', 'top': True, 'select': None}
    }
    e.insert('Illegal goal')
    # New goal must not be inserted because previous selection is reset after the view switching
    e.next_view()
    assert e.all(keys='name,top,select') == {
        1: {'name': 'Root', 'top': False, 'select': None},
        2: {'name': 'Top 1', 'top': True, 'select': 'select'},
        3: {'name': 'Top 2', 'top': True, 'select': None},
    }


def test_selection_cache_should_be_reset_after_view_switch():
    g = Goals('Root')
    # 1 -> 2 -> 3 -> .. -> 10 -> 11
    for i in range(10):
        g.add(str(i+2), i+1)
    g.add('Also top', 1)
    e = Enumeration(g)
    e.select(1)
    e.next_view()
    assert e.all('name,select') == {
        1: {'name': '11', 'select': 'select'},
        2: {'name': 'Also top', 'select': None},
    }
    e.select(2)
    assert e.all('name,select') == {
        1: {'name': '11', 'select': 'prev'},
        2: {'name': 'Also top', 'select': 'select'},
    }


def test_top_view_may_be_empty():
    e = Enumeration(Goals('closed'))
    e.toggle_close()
    e.next_view()
    assert e.all() == {}


def test_simple_top_enumeration_workflow():
    e = Enumeration(Goals('root'))
    e.add('1')
    e.add('2')
    e.select(2)
    e.next_view()
    e.select(2)
    assert e.all() == {
        1: {'name': '1'},
        2: {'name': '2'}
    }


def test_open_view_may_be_empty():
    e = Enumeration(Goals('closed'))
    e.toggle_close()
    assert e.all() == {}


def test_simple_open_enumeration_workflow():
    e = Enumeration(Goals('Root'))
    e.add('1')
    e.add('2')
    e.select(2)
    assert e.all(keys='name,select,open,edge') == {
        1: {'name': 'Root', 'select': 'prev', 'open': True, 'edge': [2, 3]},
        2: {'name': '1', 'select': 'select', 'open': True, 'edge': []},
        3: {'name': '2', 'select': None, 'open': True, 'edge': []},
    }
    e.toggle_close()
    assert e.all(keys='name,select,open,edge') == {
        1: {'name': 'Root', 'select': 'select', 'open': True, 'edge': [2]},
        2: {'name': '2', 'select': None, 'open': True, 'edge': []}
    }
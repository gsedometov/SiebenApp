# coding: utf-8
import pickle
import sqlite3
from siebenapp.goaltree import Goals
from siebenapp.system import MIGRATIONS, run_migrations, load, save
from tempfile import NamedTemporaryFile


def test_initial_migration_on_empty_db():
    conn = sqlite3.connect(':memory:')
    cur = conn.cursor()
    run_migrations(conn, MIGRATIONS[:1])
    cur.execute('select version from migrations')
    version = cur.fetchone()[0]
    assert version == 0


def test_skip_passed_migrations():
    conn = sqlite3.connect(':memory:')
    cur = conn.cursor()
    run_migrations(conn, MIGRATIONS[:1])
    run_migrations(conn, MIGRATIONS[:1])
    cur.execute('select version from migrations')
    version = cur.fetchone()[0]
    assert version == 0


def test_last_known_migration():
    conn = sqlite3.connect(':memory:')
    cur = conn.cursor()
    run_migrations(conn)
    cur.execute('select version from migrations')
    version = cur.fetchone()[0]
    assert version == 1


def setup_sample_db(conn):
    cur = conn.cursor()
    sample_goals = [(1, 'Root', True), (2, 'A', True), (3, 'B', False)]
    cur.executemany('insert into goals values (?,?,?)', sample_goals)
    sample_edges = [(1, 2), (1, 3), (2, 3)]
    cur.executemany('insert into edges values (?,?)', sample_edges)
    sample_selects = [('selection', 2), ('previous_selection', 1)]
    cur.executemany('insert into selection values (?,?)', sample_selects)
    conn.commit()
    cur.close()


def test_restore_goals_from_db():
    file_name = NamedTemporaryFile().name
    conn = sqlite3.connect(file_name)
    run_migrations(conn)
    setup_sample_db(conn)
    conn.close()
    actual_goals = load(file_name)
    expected_goals = Goals('Root')
    expected_goals.add('A')
    expected_goals.add('B')
    expected_goals.select(2)
    expected_goals.hold_select()
    expected_goals.select(3)
    expected_goals.toggle_link()
    expected_goals.select(3)
    expected_goals.toggle_close()
    expected_goals.select(2)
    assert expected_goals.all(keys='name,edge,open,select') == \
            actual_goals.all(keys='name,edge,open,select')


def test_load_from_missing_file():
    file_name = NamedTemporaryFile().name
    expected_goals = Goals('Rename me')
    new_goals = load(file_name)
    assert new_goals.all(keys='open,name,edge,select') == \
            expected_goals.all(keys='open,name,edge,select')


def test_load_from_pickle_dump():
    file_name = NamedTemporaryFile().name
    goals = Goals('Root')
    goals.add('Top')
    goals.add('Middle')
    goals.select(3)
    goals.hold_select()
    goals.select(2)
    goals.toggle_link()
    goals.add('Closed')
    goals.select(4)
    goals.toggle_close()
    with open(file_name, 'wb') as f:
        pickle.dump(goals, f)
    new_goals = load(file_name)
    assert goals.all(keys='open,name,edge,select') == new_goals.all(keys='open,name,edge,select')


def test_save_and_load():
    file_name = NamedTemporaryFile().name
    goals = Goals('Root')
    goals.add('Top')
    goals.add('Middle')
    goals.select(3)
    goals.hold_select()
    goals.select(2)
    goals.toggle_link()
    goals.add('Closed')
    goals.select(4)
    goals.toggle_close()
    save(goals, file_name)
    new_goals = load(file_name)
    assert goals.all(keys='open,name,edge,select') == new_goals.all(keys='open,name,edge,select')

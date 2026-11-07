import sqlite3, os
from pathlib import Path

def connect(path):
    if path != ':memory:':
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(path, timeout=10)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON')
    c.executescript('CREATE TABLE IF NOT EXISTS ideas(id INTEGER PRIMARY KEY,title TEXT NOT NULL); CREATE TABLE IF NOT EXISTS votes(idea INTEGER REFERENCES ideas(id),voter TEXT,UNIQUE(idea,voter));')
    return c

def run(p, db_path=None):
    path = db_path or ':memory:'
    c = connect(path)
    try:
        action = p.get('action', 'demo')
        if action == 'demo':
            for title in ['Export project reports', 'Keyboard shortcuts', 'Offline reading mode']:
                c.execute('INSERT INTO ideas(title) VALUES(?)', (title,))
        elif action == 'create':
            title = p.get('title', '').strip()
            if not 3 <= len(title) <= 100:
                raise ValueError('Title must have 3–100 characters')
            c.execute('INSERT INTO ideas(title) VALUES(?)', (title,))
        elif action == 'vote':
            voter = p.get('voter', '')
            idea = p.get('id')
            if not isinstance(voter, str) or not 8 <= len(voter) <= 80:
                raise ValueError('Voter ID must have 8–80 characters')
            if not c.execute('SELECT id FROM ideas WHERE id=?', (idea,)).fetchone():
                raise ValueError('Idea not found')
            c.execute('INSERT OR IGNORE INTO votes(idea,voter) VALUES(?,?)', (idea, voter))
        elif action != 'list':
            raise ValueError('Unknown action')
        c.commit()
        rows = c.execute('SELECT i.id,i.title,COUNT(v.voter) AS votes FROM ideas i LEFT JOIN votes v ON i.id=v.idea GROUP BY i.id ORDER BY votes DESC,i.id').fetchall()
        return {'ideas': [dict(r) for r in rows]}
    finally:
        c.close()

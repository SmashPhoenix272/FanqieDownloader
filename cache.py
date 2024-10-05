import sqlite3
import json
import time

class NovelCache:
    def __init__(self):
        self.db_path = 'novel_cache.db'
        self._create_tables()

    def _create_tables(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS novels (
                    novel_id TEXT PRIMARY KEY,
                    info TEXT,
                    last_updated INTEGER
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chapters (
                    novel_id TEXT,
                    chapter_id TEXT,
                    content TEXT,
                    last_updated INTEGER,
                    PRIMARY KEY (novel_id, chapter_id)
                )
            ''')
            conn.commit()

    def get_cached_novel_info(self, novel_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT info, last_updated FROM novels WHERE novel_id = ?', (novel_id,))
            result = cursor.fetchone()
            if result:
                return json.loads(result[0]), result[1]
            return None, None

    def update_novel_cache(self, novel_id, info):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            current_time = int(time.time())
            cursor.execute('INSERT OR REPLACE INTO novels (novel_id, info, last_updated) VALUES (?, ?, ?)',
                           (novel_id, json.dumps(info), current_time))
            conn.commit()

    def is_chapter_cached(self, novel_id, chapter_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM chapters WHERE novel_id = ? AND chapter_id = ?', (novel_id, chapter_id))
            return bool(cursor.fetchone())

    def get_cached_chapter(self, novel_id, chapter_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT content, last_updated FROM chapters WHERE novel_id = ? AND chapter_id = ?', (novel_id, chapter_id))
            result = cursor.fetchone()
            if result:
                return result[0], result[1]
            return None, None

    def update_chapter_cache(self, novel_id, chapter_id, content):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            current_time = int(time.time())
            cursor.execute('''
                INSERT OR REPLACE INTO chapters (novel_id, chapter_id, content, last_updated)
                VALUES (?, ?, ?, ?)
            ''', (novel_id, chapter_id, content, current_time))
            conn.commit()

    def get_all_cached_chapters(self, novel_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT chapter_id, content FROM chapters WHERE novel_id = ?', (novel_id,))
            return {row[0]: row[1] for row in cursor.fetchall()}
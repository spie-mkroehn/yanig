from typing import List
from core import ComponentResultObject
from api import BaseApi
import sqlite3
import os
import json


class SQLiteDB(BaseApi):
    client_path: str
    client_table: str

    def _ensure_db_and_table(self):
        # Create DB file and table if not exist
        if not os.path.exists(self.client_path):
            open(self.client_path, 'a').close()
        conn = sqlite3.connect(self.client_path)
        c = conn.cursor()
        c.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.client_table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                answers TEXT,
                correct_answer INTEGER
            )
        ''')
        conn.commit()
        conn.close()

    def write(self, output:List[ComponentResultObject]):
        self._ensure_db_and_table()
        conn = sqlite3.connect(self.client_path)
        c = conn.cursor()
        for obj in output:
            datas = json.dumps(obj)
            answers = ""
            correct_answer = -1
            for i in range(len(datas["answers"])):
                answers += f"{datas['answers'][i]['text']}|"
                if datas["answers"][i]["is_correct"]:
                    correct_answer = i
            c.execute(f'''
                INSERT INTO {self.client_table} (question, answers, correct_answer)
                VALUES (?, ?, ?)
            ''', (
                datas["question"],
                answers,
                correct_answer
            ))
        conn.commit()
        conn.close()

    def retrieve(self, input:List[ComponentResultObject])->List[ComponentResultObject]:
        self._ensure_db_and_table()
        conn = sqlite3.connect(self.client_path)
        c = conn.cursor()
        results = []
        for obj in input:
            orig_text = obj["content"]["original_text"]
            if orig_text:
                c.execute(f'''SELECT question, answers, correct_answer FROM {self.client_table} WHERE original_text = ?''', (orig_text,))
                rows = c.fetchall()
                for row in rows:
                    new_obj = ComponentResultObject()
                    new_obj.source = row[0]
                    new_obj.original_text = orig_text
                    new_obj.result_text = row[1]  # DB original_text
                    new_obj.publish_date = row[3]
                    new_obj.keywords = row[4]
                    new_obj.category = row[5]
                    results.append(new_obj)
        conn.close()
        return results

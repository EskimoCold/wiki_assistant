# satisfied:
#     0 - False
#     1 - True
#     2 - Don't voted

import sqlite3

def create_db() -> None:
    connect = sqlite3.connect("qna.db")
    cursor = connect.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_history(
            id INTEGER,
            question STRING,
            answer STRING,
            satisfied INTEGER
        )
        """
    )
    connect.commit()   


def connect_db():
    connect = sqlite3.connect("qna.db")
    cursor = connect.cursor()

    return connect, cursor


def save_q_and_a(question:str, answer:str, chat_id:int):
    connect, cursor = connect_db()
    cursor.execute("INSERT INTO user_history VALUES(?,?,?,?);", [chat_id, question, answer, 3])
    connect.commit()
    connect.close()


def update_satisfied(chat_id:int, satisfied:bool):
    connect, cursor = connect_db()
    cursor.execute("UPDATE user_history SET satisfied=? WHERE id=?", [int(satisfied), chat_id])
    connect.commit()
    connect.close()

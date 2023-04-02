import MySQLdb
from flask_login import UserMixin
import config

def db_connect():
    return MySQLdb.connect(host = config.HOST,
    user = config.USERNAME,
    passwd = config.PASSWORD,
    db = config.DB_NAME)

def get_all_users():
    connect_to_db = db_connect()
    cursor = connect_to_db.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

def get_one_user(user_id):
    connect_to_db = db_connect()
    cursor = connect_to_db.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = '{user_id}'")
    return cursor.fetchone()

def user_login_settings(email_or_username, password):
    connect_to_db = db_connect()
    cursor = connect_to_db.cursor()
    cursor.execute(f"SELECT * FROM users WHERE email = '{email_or_username}' OR username = '{email_or_username}'")
    user = cursor.fetchone()
    if user[4] == password:
        return user

    return False

def get_user_haves(user_id):
    connect_to_db = db_connect()
    cursor = connect_to_db.cursor()
    cursor.execute(f"SELECT * FROM haves WHERE user_id = '{user_id}' ORDER BY id DESC")
    return cursor.fetchall()

class User(UserMixin):
    def __init__(self, id):
        self.id = id
        user_information = get_one_user(id)
        self.name = user_information[1]
        self.email = user_information[2]
        self.username = user_information[3]
        self.password = user_information[4]

    def __repr__(self):
        return "%d/%s/%s/%s/%s" % (self.id, self.name, self.email, self.username, self.password)

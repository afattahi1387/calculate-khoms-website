import MySQLdb
from flask_login import UserMixin
from decimal import Decimal
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

def user_exists(email, username, password):
    connect_to_db = db_connect()
    cursor = connect_to_db.cursor()
    cursor.execute(f'''
        SELECT * FROM users WHERE email = '{email}' OR username = '{username}' OR password = '{password}'
    ''')

    if cursor.rowcount != 1:
        return False

    userRow = cursor.fetchone()
    repeated_fields = []
    if email == userRow[2]:
        repeated_fields.append('ایمیل')

    if username == userRow[3]:
        repeated_fields.append('نام کاربری')

    if password == userRow[4]:
        repeated_fields.append('رمز عبور')

    return repeated_fields

def get_user_haves(user_id):
    connect_to_db = db_connect()
    cursor = connect_to_db.cursor()
    cursor.execute(f"SELECT * FROM haves WHERE user_id = '{user_id}' ORDER BY id DESC")
    return cursor.fetchall()

def count_user_haves(user_id, have_type = None):
    connect_to_db = db_connect()
    cursor = connect_to_db.cursor()
    query = f"SELECT * FROM haves WHERE user_id = '{user_id}'"
    if have_type:
        query += f" AND type = '{have_type}'"

    query += " ORDER BY id DESC"
    cursor.execute(query)
    return cursor.rowcount

def get_one_have(have_id):
    connect_to_db = db_connect()
    cursor = connect_to_db.cursor()
    cursor.execute(f"SELECT * FROM haves WHERE id = {have_id}")
    return cursor.fetchone()

def user_register(user_info):
    connect_to_db = db_connect()
    cursor = connect_to_db.cursor()
    user_info['full_name'] = user_info['first_name'] + ' ' + user_info['last_name']
    cursor.execute(f'''
        INSERT INTO users VALUES (NULL, '{user_info["full_name"]}', '{user_info["email"]}', '{user_info["username"]}', '{user_info["password"]}')
    ''')
    last_row_id = cursor.lastrowid
    connect_to_db.commit()
    cursor.close()
    return last_row_id

def insert_have(have_information):
    connect_to_db = db_connect()
    cursor = connect_to_db.cursor()
    query = f'''
        INSERT INTO haves VALUES (NULL, '{have_information["name"]}', '{have_information["type"]}', '{have_information["user_id"]}', '{have_information["total_price"]}'
    '''
    if not have_information['remaining_amount']:
        query += ', NULL)'
    else:
        query += f", '{have_information['remaining_amount']}')"

    cursor.execute(query)
    connect_to_db.commit()
    cursor.close()
    return True

def update_have(have_id, new_have_row):
    connect_to_db = db_connect()
    cursor = connect_to_db.cursor()
    query = f"""
        UPDATE haves SET name = '{new_have_row['name']}',
        type = '{new_have_row['type']}',
        user_id = '{new_have_row['user_id']}',
        total_price = '{new_have_row['total_price']}'
    """

    if new_have_row['remaining_amount']:
        query += f", remaining_amount = '{new_have_row['remaining_amount']}'"
    else:
        query += ", remaining_amount = NULL"

    query += f" WHERE id = '{have_id}'"
    cursor.execute(query)
    connect_to_db.commit()
    cursor.close()
    return True

def delete_have(have_id):
    connect_to_db = db_connect()
    cursor = connect_to_db.cursor()
    
    cursor.execute(f'''
        DELETE FROM haves WHERE id = '{have_id}'
    ''')

    connect_to_db.commit()
    cursor.close()
    return True

def calculate_have_khoms(have_id):
    connect_to_db = db_connect()
    cursor = connect_to_db.cursor()
    cursor.execute(f"SELECT * FROM haves WHERE id = '{have_id}'")
    have_row = cursor.fetchone()
    if have_row[2] == 'money':
        return Decimal(have_row[4] / 5)

    return Decimal((have_row[4] * have_row[5]) / 5)

def calculate_total_prices(user_id):
    user_haves = get_user_haves(user_id)
    total_prices = 0
    for have in user_haves:
        if have[2] == 'commodity':
            total_prices += (have[4] * have[5])
        else:
            total_prices += have[4]

    return total_prices

def calculate_khoms_of_user_haves(user_id):
    all_haves = get_user_haves(user_id)
    khoms = 0
    for have in all_haves:
        khoms += calculate_have_khoms(have[0])

    return khoms

def add_cama_in_number(number):
    number = str(number)
    counter = 0
    new_number_string = ""
    for i in range(1, len(number) + 1):
        counter += 1
        new_number_string = number[-counter] + new_number_string
        if counter % 3 == 0 and len(number) > counter:
            new_number_string = ',' + new_number_string

    return new_number_string

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

import datetime
import sqlite3

from dateutil.relativedelta import relativedelta


class Database:
    def __init__(self, path_to_db="main.db"):
        self.path_to_db = path_to_db

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = ()
        connection = self.connection
        connection.set_trace_callback(logger)
        cursor = connection.cursor()
        data = None
        cursor.execute(sql, parameters)

        if commit:
            connection.commit()
        if fetchall:
            data = cursor.fetchall()
        if fetchone:
            data = cursor.fetchone()
        connection.close()
        return data

    def create_table_subs(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Subs (
            subs_id int NOT NULL,
            month_subs int,
            price int,
            PRIMARY KEY (subs_id)
            );
        """
        self.execute(sql, commit=True)

    def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
            telegram_id int,
            username text NOT NULL,
            subs int NOT NULL,
            date_begin date NULL,
            date_end date NULL,
            subs_id int NULL,
            PRIMARY KEY (telegram_id),
            FOREIGN KEY (subs_id) REFERENCES Subs (subs_id) 
            );
        """
        self.execute(sql, commit=True)

    def create_table_free_treal(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Treal (
            treal_on int NOT NULL,
            date_begin date NULL,
            date_end date NULL,
            PRIMARY KEY (treal_on)
            );
        """
        self.execute(sql, commit=True)

    def create_table_link_to_subs(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Links (
            link text NOT NULL,
            telegram_id int NOT NULL,
            PRIMARY KEY (link),
            FOREIGN KEY (telegram_id) REFERENCES Users (telegram_id) 
            );
        """
        self.execute(sql, commit=True)

    def create_table_sale(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Sale (
            sale_percent int NOT NULL,
            date_begin date NOT NULL,
            date_end date NOT NULL,
            about_sale text NOT NULL,
            PRIMARY KEY (date_begin)
            );
        """
        self.execute(sql, commit=True)

    def create_table_used_hash(self):
        sql = """
           CREATE TABLE IF NOT EXISTS Hash (
               hash_trans text NOT NULL,
               PRIMARY KEY (hash_trans)
               );
           """
        self.execute(sql, commit=True)

    def create_schedule(self):
        sql = """
            CREATE TABLE IF NOT EXISTS Schedule (
                id integer not null primary key autoincrement,
                telegram_id int NOT NULL,
                date_of_alarm date NOT NULL
                );
            """
        self.execute(sql, commit=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ?" for item in parameters
        ])
        return sql, tuple(parameters.values())

    def add_user(self, telegram_id: int, duration_subs: str, username: str):
        if duration_subs == "1 год" or duration_subs == "1 год со скидкой":
            subs_id = 4
        elif duration_subs == "6 месяцев" or duration_subs == "6 месяцев со скидкой":
            subs_id = 3
        elif duration_subs == "4 месяца" or duration_subs == "4 месяца со скидкой":
            subs_id = 2
        else:
            subs_id = 1
        sql = """
        INSERT INTO Users(telegram_id, subs, subs_id, username) VALUES(?, ?, ?, ?)
        """
        self.execute(sql, parameters=(int(telegram_id), 0, int(subs_id), username), commit=True)

    def select_user(self, telegram_id):
        sql = "SELECT * FROM Users WHERE telegram_id=?"
        return self.execute(sql, parameters=(telegram_id,), fetchone=True)

    def select_user_by_username(self, username):
        sql = "SELECT * FROM Users WHERE username=?"
        return self.execute(sql, parameters=(username,), fetchone=True)

    # вот эта хрень нужна на первое время, потому что нет у меня ид пользователей, есть только юзернеймы. Потом уберу
    def edit_user_telegram_id(self, username: str, telegram_id: int):
        sql = """
                UPDATE Users SET telegram_id=? WHERE username=?
                """
        self.execute(sql, parameters=(int(telegram_id), username), commit=True)

    def select_user_subs_id(self, telegram_id):
        sql = "SELECT subs_id FROM Users WHERE telegram_id=?"
        return self.execute(sql, parameters=(telegram_id,), fetchone=True)

    def select_subs(self, subs_id):
        sql = "SELECT month_subs FROM Subs WHERE subs_id=?"
        return self.execute(sql, parameters=(subs_id,), fetchone=True)

    def edit_user_subs(self, telegram_id: int, begin_date):
        user_subs_id = self.select_user(telegram_id)[5]
        duration = self.select_subs(user_subs_id)[0]
        date_end = datetime.datetime.strptime(begin_date, "%Y-%m-%d") + relativedelta(months=+duration)
        sql = """
        UPDATE Users SET date_begin=?, date_end=?, subs=1 WHERE telegram_id=?
        """
        self.execute(sql, parameters=(begin_date, date_end.strftime("%Y-%m-%d"), int(telegram_id)), commit=True)

    def add_sale(self, sale_percent, date_begin, date_end, about_sale):
        sql = """
                INSERT INTO Sale(sale_percent, date_begin, date_end, about_sale) VALUES(?, ?, ?, ?)
                """
        self.execute(sql, parameters=(sale_percent, date_begin, date_end, about_sale), commit=True)

    def delete_sale(self, date_begin):
        self.execute("DELETE FROM Sale WHERE date_begin=?", parameters=(date_begin,), commit=True)

    def select_sales(self):
        sql = "SELECT * FROM Sale"
        return self.execute(sql, fetchall=True)

    def edit_price(self, duration, price):
        sql = """
                UPDATE Subs SET price=? WHERE month_subs=?
                """
        self.execute(sql, parameters=(int(price), int(duration)), commit=True)

    def treal_on(self, begin_date):
        end_date = datetime.datetime.strptime(begin_date, "%Y-%m-%d") + relativedelta(days=14)
        sql = """
              UPDATE Treal SET date_begin=?, treal_on=1, date_end=? WHERE treal_on=0
              """
        self.execute(sql, parameters=(begin_date, end_date.strftime("%Y-%m-%d")), commit=True)

    def select_prices(self):
        sql = "SELECT * FROM Subs"
        return self.execute(sql, fetchall=True)

    def treal_mode(self):
        sql = "SELECT * FROM Treal"
        return self.execute(sql, fetchone=True)

    def select_price(self, duration_subs: str):
        # да, тут нормальный чел сделает запрос и узнает ид подписки, но ну тут-то было)
        if duration_subs == "1 год" or duration_subs == "1 год со скидкой":
            subs_id = 4
        elif duration_subs == "6 месяцев" or duration_subs == "6 месяцев со скидкой":
            subs_id = 3
        elif duration_subs == "4 месяца" or duration_subs == "4 месяца со скидкой":
            subs_id = 2
        else:
            subs_id = 1
        sql = "SELECT price FROM Subs WHERE subs_id=?"
        return self.execute(sql, parameters=(subs_id,), fetchone=True)

    def edit_user_duration_subs(self, telegram_id: int, duration_subs: str):
        if duration_subs == "1 год" or duration_subs == "1 год со скидкой":
            subs_id = 4
        elif duration_subs == "6 месяцев" or duration_subs == "6 месяцев со скидкой":
            subs_id = 3
        elif duration_subs == "4 месяца" or duration_subs == "4 месяца со скидкой":
            subs_id = 2
        else:
            subs_id = 1
        sql = """
        UPDATE Users SET subs_id=? WHERE telegram_id=?
        """
        self.execute(sql, parameters=(int(subs_id), int(telegram_id)), commit=True)

    def add_hash(self, hash_trans):
        sql = """
                INSERT INTO Hash(hash_trans) VALUES(?)
                """
        self.execute(sql, parameters=(hash_trans,), commit=True)

    def select_hash(self, hash_trans):
        sql = "SELECT * FROM Hash WHERE hash_trans=?"
        return self.execute(sql, parameters=(hash_trans,), fetchone=True)

    def add_alarm_for_users(self, telegram_id, date_alarm):
        sql = """
              INSERT INTO Schedule(telegram_id, date_of_alarm) VALUES(?, ?)
              """
        self.execute(sql, parameters=(telegram_id, date_alarm.strftime("%Y-%m-%d")), commit=True)

    def delete_alarm_for_users(self, telegram_id):
        self.execute("DELETE FROM Schedule WHERE telegram_id=?", parameters=(telegram_id,), commit=True)

    def select_alarm_for_users(self, now):
        sql = "SELECT * FROM Schedule WHERE date_of_alarm=?"
        return self.execute(sql, parameters=(now.strftime("%Y-%m-%d"),), fetchall=True)

    def select_users(self):
        sql = """
        SELECT * FROM Users
        """
        return self.execute(sql, fetchall=True)

    def select_sales_with_date(self, yesterday):
        sql = "SELECT * FROM Sale WHERE date_end=?"
        return self.execute(sql, parameters=(yesterday,), fetchall=True)

    def treal_mode_with_date(self, yesterday):
        sql = "SELECT * FROM Treal WHERE date_end=?"
        return self.execute(sql, parameters=(yesterday,), fetchone=True)

    def treal_off(self):
        sql = """
              UPDATE Treal SET date_begin=null, treal_on=0, date_end=null WHERE treal_on=1
              """
        self.execute(sql, commit=True)

    def add_treal_user(self, telegram_id, username):
        date_end = self.treal_mode()[2]
        sql = """
                INSERT INTO Users(telegram_id, subs, date_end, username) VALUES(?, ?, ?, ?)
                """
        self.execute(sql, parameters=(int(telegram_id), 0, date_end, username), commit=True)

    def select_users_with_treal(self, yesterday):
        sql = "SELECT * FROM Users WHERE date_end=? and subs_id=null and date_begin=null and subs=0"
        return self.execute(sql, parameters=(yesterday,), fetchall=True)

    def delete_user_all_null(self, telegram_id):
        self.execute("DELETE FROM Users WHERE telegram_id=?", parameters=(telegram_id,), commit=True)

    def select_users_with_date(self, yesterday):
        sql = "SELECT * FROM Users WHERE date_end=? and subs=1"
        return self.execute(sql, parameters=(yesterday,), fetchall=True)

    def select_price_to_user(self, telegram_id):
        sql = "SELECT subs_id FROM Users WHERE telegram_id=?"
        subs_id = self.execute(sql, parameters=(telegram_id,), fetchone=True)
        sql = "SELECT price FROM Subs WHERE subs_id=?"
        return self.execute(sql, parameters=(int(subs_id[0]),), fetchone=True)

    def all_users(self):
        sql = "SELECT *  FROM Users"
        return self.execute(sql, fetchall=True)


def logger(statement):
    print(f"""
_____________________________________________________        
Executing: 
{statement}
_____________________________________________________
""")

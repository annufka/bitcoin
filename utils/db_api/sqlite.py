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
            month_subs int NOT NULL,
            price int NOT NULL,
            PRIMARY KEY (subs_id)
            );
        """
        self.execute(sql, commit=True)

    def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
            telegram_id int NOT NULL,
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

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ?" for item in parameters
        ])
        return sql, tuple(parameters.values())

    def add_user(self, telegram_id: int, duration_subs: str):
        if duration_subs == "1 год" or duration_subs == "1 год со скидкой":
            subs_id = 4
        elif duration_subs == "6 месяцев" or duration_subs == "6 месяцев со скидкой":
            subs_id = 3
        elif duration_subs == "4 месяца" or duration_subs == "4 месяца со скидкой":
            subs_id = 2
        else:
            subs_id = 1
        sql = """
        INSERT INTO Users(telegram_id, subs, subs_id) VALUES(?, ?, ?)
        """
        self.execute(sql, parameters=(int(telegram_id), 0, int(subs_id)), commit=True)

    def select_user(self, telegram_id):
        sql = "SELECT * FROM Users WHERE telegram_id=?"
        return self.execute(sql, parameters=(telegram_id,), fetchone=True)

    def select_subs(self, subs_id):
        sql = "SELECT month_subs FROM Subs WHERE subs_id=?"
        return self.execute(sql, parameters=(subs_id,), fetchone=True)

    def edit_user_subs(self, telegram_id: int, begin_date):
        user_subs_id = self.select_user(telegram_id)[4]
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
        sql = """
              UPDATE Treal SET date_begin=?, treal_on=1 WHERE treal_on=0
              """
        self.execute(sql, parameters=(begin_date,), commit=True)

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

    # def count_users(self):
    #     return self.execute("SELECT COUNT(*) FROM Users;", fetchone=True)


def logger(statement):
    print(f"""
_____________________________________________________        
Executing: 
{statement}
_____________________________________________________
""")

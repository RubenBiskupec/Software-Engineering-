import sys
import mysql
import configparser
import hashlib
from mysql.connector import Error
from datetime import datetime


def load_credentials():
    config = configparser.ConfigParser()
    config.read("credentials.ini")
    db_credentials = {'username': config["database"]["db_username"],
                      'password': config["database"]["db_password"],
                      'hostname': config["database"]["db_hostname"],
                      'database': config["database"]["db_database"]}
    return db_credentials


class DataSender:
    def __init__(self):
        self.db_credentials = load_credentials()
        self.connection = self.initialize_connection()

    def __del__(self):
        self.close_connection()

    def initialize_connection(self):
        connection = mysql.connector.connect(host=self.db_credentials['hostname'],
                                             password=self.db_credentials['password'],
                                             user=self.db_credentials['username'],
                                             database=self.db_credentials['database'])
        return connection

    def close_connection(self):
        if self.connection.is_connected():
            self.connection.close()
            print("Mysql connection closed")

    def send_transaction_info(self, transaction):
        # local_record = {
        #     'journal_record_no': record_no,
        #     'journal_record_date': record_date,
        #     'journal_record_cashier': record_cashier,
        #     'journal_record_type': record_type,
        #     'journal_record_aborted': aborted_sale,
        #     'journal_record_products': products,
        # }
        try:
            transaction_id = abs(hash(transaction['journal_record_date'] + transaction['journal_record_no']))
            mysql_select_query = """SELECT * FROM transaction WHERE receipt_number = '%d'""" % transaction_id
            cursor = self.connection.cursor(buffered=True)
            cursor.execute(mysql_select_query)
            if cursor.rowcount == 0:
                transaction_datetime = datetime.strptime(transaction['journal_record_date'], '%Y-%m-%d %H:%M:%S')
                mysql_insert_query = (
                        """INSERT INTO transaction (date_time, receipt_number) VALUES ('%s', '%d')"""
                        % (
                            transaction_datetime,
                            transaction_id
                        )
                )
                cursor.execute(mysql_insert_query)
                self.connection.commit()
                print(cursor.rowcount, "Record inserted successfully")
                cursor.close()
            else:
                print("already in the database")
                cursor.close()
        except Error as error:
            print("Failed to insert record into table {}".format(error), file=sys.stderr)

    def send_product_info(self, product):
        try:
            mysql_select_query = """SELECT * FROM product_info WHERE plu = '%d'""" % int(
                product["product_plu"]
            )
            cursor = self.connection.cursor(buffered=True)
            cursor.execute(mysql_select_query)
            if cursor.rowcount == 0:
                mysql_insert_query = (
                        """INSERT INTO product_info (plu, name, selling_price) VALUES ('%d', '%s', '%f')"""
                        % (
                            int(product["product_plu"]),
                            product["product_name"],
                            float(product["product_price"].replace(",", ".")),
                        )
                )
                cursor.execute(mysql_insert_query)
                self.connection.commit()
                print(cursor.rowcount, "Record inserted successfully")
                cursor.close()
            else:
                print("already in the database")
                cursor.close()
        except Error as error:
            print("Failed to insert record into table {}".format(error), file=sys.stderr)


def send_transaction_info(cp):
    try:

        connection = mysql.connector.connect()
        print("card_usage_date = ", cp["cp_date"])
        print("card_transaction_id = ", cp["cp_transaction"])
        print("card_total_amount = ", cp["cp_drawer_amount"])
        print("card_serial =", cp["cp_card_serial_number"])
        from datetime import datetime

        datetim = datetime.strptime(cp["cp_date"], "%d/%m/%Y %H:%M")
        mysql_insert_query = (
                """INSERT INTO transaction (date_time, receipt_number, total_amount, card_serial) VALUES ('%s', '%d', '%f', '%d')"""
                % (
                    datetim,
                    int(cp["cp_transaction"]),
                    float(cp["cp_drawer_amount"].replace(",", ".")),
                    int(cp["cp_card_serial_number"]),
                )
        )
        cursor = connection.cursor()
        cursor.execute(mysql_insert_query)
        connection.commit()
        print(cursor.rowcount, "Record inserted succesfully")
        cursor.close()
    except mysql.connector.Error as error:
        print("Failed to insert record into table {}".format(error))
    finally:
        if connection.is_connected():
            connection.close()
            print("Mysql connection closed")

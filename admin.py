import mysql.connector
from mysql.connector import Error

def admin(name, username, password):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='pln_sipekat',
            user='root',
            password=''
        )

        if connection.is_connected():
            cursor = connection.cursor()
            query = "INSERT INTO admin (name, username, password) VALUES (%s, %s, %s)"
            cursor.execute(query, (name, username, password))
            connection.commit()
            print("Admin data inserted successfully")

    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

if __name__ == "__main__":
    name = "Admin PLN"
    username = "admin-pln"
    password = "admin@pln"
    admin(name, username, password)

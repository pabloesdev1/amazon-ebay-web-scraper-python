import mysql.connector as mysql

def connect():
    try:
        connection = mysql.connect(
            host = 'localhost',
            user = 'root',
            password = '',
            database = 'web_scraping'
        )
        print("Se ha conectado a la base de datos")
        return connection
    except mysql.Error as err:
        print("Ha ocurrido un error: "+err)

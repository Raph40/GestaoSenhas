import mysql.connector
from infdotenv import host, user, password, database

class sqlConnection():
    def Connection(self):
        mydb = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        return mydb
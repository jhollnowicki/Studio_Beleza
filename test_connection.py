import mysql.connector
from db import get_connection

def test_connection():
    connection = get_connection()
    if connection:
        print("Conexão com o banco de dados estabelecida com sucesso!")
        connection.close()  # Feche a conexão após o teste
    else:
        print("Falha ao conectar com o banco de dados.")

if __name__ == "__main__":
    test_connection()

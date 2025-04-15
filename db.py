import mysql.connector

def get_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',  # Altere conforme necessário
            user='root',  # Altere conforme necessário
            password='Lnv13301381@',  # Coloque sua senha aqui
            database='studio_beleza'  # O nome do seu banco de dados
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Erro de conexão: {err}")
        return None

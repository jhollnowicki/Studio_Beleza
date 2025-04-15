import mysql.connector
import os
from dotenv import load_dotenv


load_dotenv()

def get_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'), 
            user=os.getenv('DB_USER'),  
            password=os.getenv('DB_PASSWORD'),  
            database=os.getenv('DB_NAME'), 
            
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Erro de conexão: {err}")
        return None


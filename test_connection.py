from db import get_connection

try:
    connection = get_connection()
    if connection:
        print("Conexão bem-sucedida!")
        connection.close()
    else:
        print("Erro ao conectar: conexão retornou None")
except Exception as e:
    print("Erro de conexão:", e)

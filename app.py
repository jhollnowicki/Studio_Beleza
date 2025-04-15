from flask import Flask, render_template, request, redirect, url_for
from db import get_connection
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    # Conectar ao banco de dados
    connection = get_connection()

    if not connection:
        return "Erro ao conectar ao banco de dados."

    cursor = connection.cursor()

    try:
        # Executar consulta
        cursor.execute("SELECT * FROM serviços")  # Certifique-se de que a tabela é realmente "servicos" sem acento
        services = cursor.fetchall()
    except Exception as e:
        print(f"Erro ao executar a consulta: {e}")  # Mostra o erro no terminal para depuração
        return f"Erro ao consultar o banco de dados: {e}"  # Retorna o erro específico no navegador
    finally:
        # Fechar conexão
        cursor.close()
        connection.close()

    print(services)  # Para verificar se os dados estão sendo retornados

    # Passar os dados para o template
    return render_template('index.html', services=services)

@app.route('/enviar', methods=['POST'])
def enviar_agendamento():
    nome = request.form['nome']
    email = request.form['email']
    telefone = request.form['telefone']
    servico_id = request.form['servico_id']
    data_hora = request.form['data_hora']

    connection = get_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO agendamentos (nome_cliente, email, telefone, servico_id, data_hora)
            VALUES (%s, %s, %s, %s, %s)
        """, (nome, email, telefone, servico_id, data_hora))
        connection.commit()
        cursor.close()
        connection.close()

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)

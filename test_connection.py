from flask import Flask, render_template, request, redirect, url_for, jsonify 
from db import get_connection
import logging
from dotenv import load_dotenv
import os
from datetime import datetime


load_dotenv()

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def home():
    logger.info("Iniciando conexão com o banco...")
    connection = get_connection()

    if not connection:
        logger.error("Falha na conexão com o banco!")
        return render_template('erro.html', mensagem="Erro ao conectar ao banco de dados"), 500

    try:
        with connection.cursor() as cursor:
            logger.info("Executando consulta de serviços...")
            cursor.execute("SELECT * FROM `serviços`")  # Escapando o nome da tabela
            services = cursor.fetchall()
            logger.info(f"Serviços encontrados: {len(services)}")
            
        return render_template('index.html', services=services)
        
    except Exception as e:
        logger.error(f"Erro na consulta: {str(e)}")
        return render_template('erro.html', mensagem=f"Erro no servidor: {str(e)}"), 500
        
    finally:
        connection.close()
        logger.info("Conexão fechada")

@app.route('/horarios_disponiveis', methods=['POST'])
def horarios_disponiveis():
    dados = request.get_json()
    data = dados['data']
    servico_id = dados['servico_id']

    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(""" 
                           SELECT data_hora FROM agendamentos
                           WHERE servico_id = %s AND DATE(data_hora) = %s
                           """, (servico_id, data))
            horarios_agendados = cursor.fetchall()

            return jsonify({'horarios_agendados': [h[0].strftime("%H:%M") for h in horarios_agendados]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close() 
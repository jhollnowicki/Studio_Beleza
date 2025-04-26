from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from db import get_connection, get_dict_cursor
import logging
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'studio_beleza')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'Lnv13301381@'



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        if usuario == 'admin' and senha == '1234':
            session['usuario'] = usuario
            return redirect(url_for('painel'))
        else:
            return render_template('login.html', erro="Usuário ou senha invalidos!")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

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
            cursor.execute("SELECT * FROM `servicos`")  # Escapando o nome da tabela
            services = cursor.fetchall()
            logger.info(f"Serviços encontrados: {len(services)}")
            
        return render_template('index.html', services=services)
        
    except Exception as e:
        logger.error(f"Erro na consulta: {str(e)}")
        return render_template('erro.html', mensagem=f"Erro no servidor: {str(e)}"), 500
        
    finally:
        connection.close()
        logger.info("Conexão fechada")



@app.route('/agendar', methods=['GET', 'POST'])
def agendar():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        nome_cliente = request.form['nome_cliente']
        telefone_cliente = request.form['telefone_cliente']
        email_cliente = request.form['email_cliente']
        servico_id = request.form['servico_id']
        data_hora = request.form['data_hora']
        
        try:
            data_hora_obj = datetime.strptime(data_hora, "%Y-%m-%d %H:%M")
        except ValueError:
            return render_template('erro.html', mensagem="Data e Hora com formato inválido."), 400

        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM agendamentos 
                    WHERE servico_id = %s AND data_hora = %s
                """, (servico_id, data_hora_obj))
                resultado = cursor.fetchone()
                if resultado[0] > 0:
                    return render_template('erro.html', mensagem="Já existe um agendamento para este serviço nesse horário."), 409
                
                cursor.execute("""
                    INSERT INTO agendamentos (nome_cliente, telefone, email, servico_id, data_hora)
                    VALUES (%s, %s, %s, %s, %s)
                """, (nome_cliente, telefone_cliente, email_cliente, servico_id, data_hora_obj))
                connection.commit()

            return redirect(url_for('painel'))
        except Exception as e:
            return render_template('erro.html', mensagem=f"Erro ao agendar: {str(e)}"), 500
        finally:
            connection.close()
    
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, nome FROM servicos")
            servicos = cursor.fetchall()  

        
        servicos_lista = [{'id': servico[0], 'nome': servico[1]} for servico in servicos]
        return render_template('agendar.html', servicos=servicos_lista)
    
    except Exception as e:
        return render_template('erro.html', mensagem=f"Erro ao carregar serviços: {str(e)}"), 500
    finally:
        connection.close()



from datetime import datetime

@app.route('/painel')
def painel():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    data_filtro = request.args.get('data_filtro')
    
    if not data_filtro:
       
        data_filtro = datetime.today().strftime('%Y-%m-%d')
    
    connection = get_connection()
    try:
        with get_dict_cursor(connection) as cursor:
            query = """
                SELECT a.id, a.nome_cliente, a.telefone, s.nome AS servico, a.data_hora, a.status
                FROM agendamentos a
                JOIN servicos s on a.servico_id = s.id
                WHERE DATE(a.data_hora) = %s
                ORDER BY a.data_hora DESC
            """
            
            params = (data_filtro,)
            
            cursor.execute(query, params)
            agendamentos = cursor.fetchall()
            
        return render_template('painel.html', agendamentos=agendamentos)
    except Exception as e:
        return render_template('erro.html', mensagem=f'Erro ao buscar agendamentos: {str(e)}')
    finally:
        connection.close()


@app.route('/atualizar_status_agendamento/<int:agendamento_id>', methods=['POST'])
def atualizar_status(agendamento_id):
    novo_status = request.form.get('status')
    
    if novo_status not in ['Aguardando', 'Confirmado', 'Cancelado', 'Realizado']:
        return render_template('error.html', mensagem="Status invalido.")
    connection = get_connection()
    try:
        with get_dict_cursor(connection) as cursor:
            cursor.execute("""
                           UPDATE agendamentos
                           SET status = %s
                           WHERE id = %s""", (novo_status, agendamento_id))
            connection.commit()
        return redirect(url_for('painel'))
    except Exception as e:
        return render_template('error.html', mensagem=f'Erro ao atualizar status: {str(e)}')
    finally:
        connection.close()


@app.route('/horarios_disponiveis', methods=['POST'])
def horarios_disponiveis():
    dados = request.get_json()
    data = dados['data']  
    servico_id = dados['servico_id']

    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            
            data_obj = datetime.strptime(data, '%Y-%m-%d').date()

          
            cursor.execute("""
                SELECT data_hora 
                FROM agendamentos
                WHERE servico_id = %s AND DATE(data_hora) = %s
            """, (servico_id, data_obj))

            horarios_agendados = cursor.fetchall()

           
            horarios_disponiveis = [h[0].strftime("%H:%M") for h in horarios_agendados]

            return jsonify({'horarios_agendados': horarios_disponiveis})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        connection.close()


@app.route('/enviar', methods=['POST'])
def enviar_agendamento():
    try:
        dados = {
            'nome': request.form['nome'],
            'email': request.form['email'],
            'telefone': request.form['telefone'],
            'servico_id': request.form['servico_id']
        }

        data = request.form['data']
        hora = request.form['hora']

        if not data or not hora:
            raise ValueError("Data ou Hora não fornecidos corretamente")

        data_hora_str = f"{data} {hora}"
        logger.info(f"Data e Hora combinadas: {data_hora_str}")

        try:
            data_hora = datetime.strptime(data_hora_str, "%Y-%m-%d %H:%M")
        except ValueError as ve:
            logger.error(f"Erro na formatação da data e hora: {ve}")
            return render_template('erro.html', mensagem="Formato de data ou hora inválido"), 400

        dados['data_hora'] = data_hora

        logger.info(f"Recebido agendamento: {dados}")
        
        connection = get_connection()
        if not connection:
            raise Exception("Sem conexão com o banco")
            
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM agendamentos
                    WHERE servico_id = %s AND data_hora = %s
                """, (dados['servico_id'], dados['data_hora']))
                resultado = cursor.fetchone()

                if resultado[0] > 0:
                    logger.warning("Agendamento duplicado detectado.")
                    return render_template('erro.html', mensagem="Já existe um agendamento para esse serviço nesse horário."), 409
                
                cursor.execute("SELECT nome FROM servicos WHERE id = %s", (dados['servico_id'],))
                servico_nome = cursor.fetchone()

                if resultado:
                    servico_nome = resultado[0]
                else:
                    raise Exception("Serviço não encontrado!")
                
                cursor.execute("""
                    INSERT INTO agendamentos 
                    (nome_cliente, email, telefone, servico_id, data_hora)
                    VALUES (%s, %s, %s, %s, %s)
                """, tuple(dados.values()))
                connection.commit()

                logger.info("Agendamento salvo com sucesso!")
                
        finally:
            connection.close()
            
        return redirect(url_for('home'))
        
    except KeyError as e:
        logger.error(f"Campo faltando: {str(e)}")
        return render_template('erro.html', mensagem=f"Dados incompletos: {str(e)}"), 400
        
    except Exception as e:
        logger.error(f"Erro no agendamento: {str(e)}")
        return render_template('erro.html', mensagem=f"Erro ao agendar: {str(e)}"), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)

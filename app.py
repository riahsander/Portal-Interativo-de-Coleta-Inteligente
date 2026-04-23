from flask import Flask, render_template, request
import sqlite3
import os
from groq import Groq
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# --- INÍCIO DA CONFIGURAÇÃO DA IA ---
# Substitua 'SUA_CHAVE_AQUI' pela sua API Key real do Groq.
# (Em um ambiente de produção real, usaríamos os.environ.get("GROQ_API_KEY") por segurança)
client = Groq(api_key=api_key)

# --- FUNÇÃO PARA INICIALIZAR O BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect('coleta.db')
    cursor = conn.cursor()
    
    # Tabela de bairros
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bairros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
    ''')
    
    # Tabela do cronograma de coleta
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cronograma (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bairro_id INTEGER,
            tipo_lixo TEXT NOT NULL,
            dia_semana TEXT NOT NULL,
            horario TEXT DEFAULT '06h às 15h',
            FOREIGN KEY(bairro_id) REFERENCES bairros(id)
        )
    ''')
    
    conn.commit()
    conn.close()

# --- ROTA 1: PÁGINA INICIAL E BUSCA (HTMX) ---
@app.route('/')
def index():
    busca = request.args.get('bairro')
    resultados = []

    if busca:
        conn = sqlite3.connect('coleta.db')
        cursor = conn.cursor()
        
        # Busca no banco usando LIKE para encontrar pedaços do nome
        cursor.execute('''
            SELECT c.tipo_lixo, c.dia_semana, c.horario
            FROM cronograma c
            JOIN bairros b ON c.bairro_id = b.id
            WHERE b.nome LIKE ?
        ''', (f'%{busca}%',))
        
        resultados = cursor.fetchall()
        conn.close()

        # Se a requisição veio do HTMX, devolvemos apenas o bloco de resultados
        if 'HX-Request' in request.headers:
            return render_template('resultados.html', resultados=resultados, busca=busca)

    # Se for um acesso normal (abrindo o site), devolve a página inteira
    return render_template('index.html')

# --- ROTA 2: GUIA DE DESCARTE ---
@app.route('/guia')
def guia():
    return render_template('guia.html')

# --- ROTA 3: ASSISTENTE VIRTUAL COM IA ---
@app.route('/perguntar-ia')
def assistente_ia():
    pergunta_usuario = request.args.get('duvida')
    
    if not pergunta_usuario:
        return "<p class='text-red-500 text-sm'>Por favor, digite sua dúvida.</p>"

    try:
        # Contexto estrito para a IA focar apenas nas regras da cidade
        contexto_campo_bom = """
        Você é um assistente virtual especialista em gestão de resíduos da cidade de Campo Bom, RS.
        Sua missão é responder dúvidas dos moradores sobre onde e como jogar o lixo fora.
        Responda SEMPRE de maneira didática, direta e educada.
        Se for dar dicas de localizações, use somente lugares que sejam em Campo Bom, RS.
        Se necessários use informações desses links: https://www.campobom.rs.gov.br/
        Algumas informações como a maneira correta de descarte correto de itens, pode buscar em outras fontes.
        Exemplos de Regras de Campo Bom:
        - Lixo Seco (Reciclável): Plástico, papel, vidro, embalagens Tetra Pak, metal. Deve estar limpo.
        - Lixo Orgânico: Restos de comida, cascas de frutas.
        - Rejeitos (Vai com o Orgânico): Papel higiênico, fraldas, fitas adesivas, guardanapos sujos.
        - Móveis e Eletrodomésticos: O morador deve chamar o serviço 'Caco Treco' da Prefeitura.
        - Pilhas, baterias e eletrônicos: O morador deve levar aos PEVs (localizados no CEMEA ou no saguão da Prefeitura).
        Se o usuário perguntar sobre datas e horários de coletas de lixo nos bairros, indique que façam a buscam barra de pesquisa do site onde você foi integrado, não diga qual o site pois o usuário já está nele.
        Se o usuário perguntar algo que não seja sobre descarte correto, diga: "Sou um assistente focado em limpeza urbana. Só posso responder sobre descarte de resíduos."
        """

        # Requisição para a API da Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": contexto_campo_bom},
                {"role": "user", "content": pergunta_usuario}
            ],
            model="llama-3.3-70b-versatile", # Modelo rápido da Meta rodando no Groq
            temperature=0.3, # Baixa temperatura garante respostas mais objetivas e reais
        )
        
        resposta = chat_completion.choices[0].message.content
        
        # Devolve a resposta pronta em HTML
        return f"""
        <div class='p-4 bg-purple-50 border border-purple-200 rounded-lg text-gray-800 shadow-sm mt-4'>
            <p class='text-sm text-purple-600 font-bold mb-1'>🤖 Assistente Virtual responde:</p>
            <p>{resposta}</p>
        </div>
        """
    
    except Exception as e:
        # Imprime o erro real no terminal do VS Code para facilitar o debug se a API Key falhar
        print(f"Erro na integração com IA: {e}")
        return "<p class='text-red-500 text-sm mt-4'>Erro ao consultar a IA. Verifique sua chave de API ou conexão.</p>"

# --- INICIALIZAÇÃO DO SERVIDOR ---
if __name__ == '__main__':
    init_db() # Garante que o banco exista sempre que o código rodar
    print("Servidor rodando! Acesse: http://127.0.0.1:5000")
    app.run(debug=True)
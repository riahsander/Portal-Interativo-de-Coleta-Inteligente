from flask import Flask, render_template, request
import sqlite3
import os
from groq import Groq
from dotenv import load_dotenv
import unicodedata

app = Flask(__name__)

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# --- INÍCIO DA CONFIGURAÇÃO DA IA ---
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# --- FUNÇÃO PARA INICIALIZAR O BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect('coleta.db')
    cursor = conn.cursor()
    
    # 1. Criação das Tabelas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bairros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
    ''')
    
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
    
    # 2. Verificação de Dados (Evita duplicados no Render)
    cursor.execute('SELECT COUNT(*) FROM bairros')
    if cursor.fetchone()[0] == 0:
        print("Populando banco de dados com os dados oficiais de Campo Bom...")
        
        # Mapeamento Completo à prova de erros
        dados_cidade = {
            # --- Lixo Seco: Segunda-feira ---
            '25 de Julho': ('Segunda-feira', 'Terça e Quinta-feira'),
            'Barrinha': ('Segunda-feira', 'Terça e Quinta-feira'),
            'Bela Vista': ('Segunda-feira', 'Terça e Quinta-feira'),
            'Celeste': ('Segunda-feira', 'Terça e Quinta-feira'),
            'Centro': ('Segunda-feira', 'Terça e Quinta-feira'),
            'Cohab Leste': ('Segunda-feira', 'Terça e Quinta-feira'),
            'Cohab Sul': ('Segunda-feira', 'Terça e Quinta-feira'),
            'Colina Deuner': ('Segunda-feira', 'Terça e Quinta-feira'),
            'Dona Augusta': ('Segunda-feira', 'Terça e Quinta-feira'),
            'Genuíno Sampaio': ('Segunda-feira', 'Terça e Quinta-feira'),
            'Jardim do Sol': ('Segunda-feira', 'Terça e Quinta-feira'),

            # --- Lixo Seco: Terça-feira ---
            'Aurora': ('Terça-feira', 'Quarta e Sexta-feira'),
            'Firenze': ('Terça-feira', 'Quarta e Sexta-feira'),
            'Imigrante Norte': ('Terça-feira', 'Quarta e Sexta-feira'),
            'Imigrante Sul': ('Terça-feira', 'Quarta e Sexta-feira'),
            'Ipiranga': ('Terça-feira', 'Quarta e Sexta-feira'),
            'Metzler': ('Terça-feira', 'Quarta e Sexta-feira'),
            'Renascer': ('Terça-feira', 'Quarta e Sexta-feira'),
            'Rio Branco': ('Terça-feira', 'Quarta e Sexta-feira'),

            # --- Lixo Seco: Quarta-feira ---
            'Bem Viver I': ('Quarta-feira', 'Terça e Quinta-feira'),
            'Bem Viver II': ('Quarta-feira', 'Terça e Quinta-feira'),
            'Esperança': ('Quarta-feira', 'Terça e Quinta-feira'),
            'Floresta': ('Quarta-feira', 'Terça e Quinta-feira'),
            'Gringos': ('Quarta-feira', 'Terça e Quinta-feira'),
            'Industrial Sul': ('Quarta-feira', 'Terça e Quinta-feira'),
            'Mônaco': ('Quarta-feira', 'Terça e Quinta-feira'),
            'Operária': ('Quarta-feira', 'Terça e Quinta-feira'),
            'Porto Blos': ('Quarta-feira', 'Terça e Quinta-feira'),
            'Sempre Unidos': ('Quarta-feira', 'Terça e Quinta-feira'),
            'Vila Nova': ('Quarta-feira', 'Terça e Quinta-feira'),
            'Vila Rica': ('Quarta-feira', 'Terça e Quinta-feira'),
            'Catleia': ('Quarta-feira', 'Terça e Quinta-feira'),
            'Dom Guilherme': ('Quarta-feira', 'Terça e Quinta-feira'),
            'Blumemburg': ('Quarta-feira', 'Terça e Quinta-feira'),

            # --- Lixo Seco: Sexta-feira ---
            'Bem Viver III': ('Sexta-feira', 'Terça e Quinta-feira'),
            'Fauth': ('Sexta-feira', 'Terça e Quinta-feira'),
            'Luz do Sol': ('Sexta-feira', 'Terça e Quinta-feira'),
            'Morada do Sol': ('Sexta-feira', 'Terça e Quinta-feira'),
            'Quatro Colônias': ('Sexta-feira', 'Terça e Quinta-feira'),
            'Santa Lúcia': ('Sexta-feira', 'Terça e Quinta-feira'),
            'Santo Antônio': ('Sexta-feira', 'Terça e Quinta-feira'),
            'Sete de Junho': ('Sexta-feira', 'Terça e Quinta-feira'),
            'União': ('Sexta-feira', 'Terça e Quinta-feira'),
            'Vale dos Sinos': ('Sexta-feira', 'Terça e Quinta-feira'),
            'Vila Brito': ('Sexta-feira', 'Terça e Quinta-feira'),
            'Vila Velha': ('Sexta-feira', 'Terça e Quinta-feira'),

            # --- Lixo Seco: Sábado ---
            'Alto Paulista': ('Sábado', 'Segunda e Quarta-feira'),
            'Paulista': ('Sábado', 'Segunda e Quarta-feira'),
            'Recanto da Paz': ('Sábado', 'Segunda e Quarta-feira'),
            'Solar do Campo': ('Sábado', 'Segunda e Quarta-feira'),
            'Zona Expansão Urbana Leste': ('Sábado', 'Segunda e Quarta-feira'),
            'Zona Industrial Norte': ('Sábado', 'Quartas e Sextas-feira'),
            'Zona Rural Norte': ('Sábado', 'Quartas e Sextas-feira')
        }

        # 3. Inserção Dinâmica
        for nome_bairro, horarios in dados_cidade.items():
            cursor.execute('INSERT INTO bairros (nome) VALUES (?)', (nome_bairro,))
            bairro_id = cursor.lastrowid
            
            # Insere Lixo Seco
            cursor.execute('''
                INSERT INTO cronograma (bairro_id, tipo_lixo, dia_semana) 
                VALUES (?, ?, ?)''', (bairro_id, 'Lixo Seco (Reciclável)', horarios[0]))
            
            # Insere Lixo Orgânico
            cursor.execute('''
                INSERT INTO cronograma (bairro_id, tipo_lixo, dia_semana) 
                VALUES (?, ?, ?)''', (bairro_id, 'Lixo Orgânico / Comum', horarios[1]))

    conn.commit()
    conn.close()

# GARANTA que o init_db() rode logo que o arquivo for lido pelo servidor:
init_db()

# --- ROTA 1: PÁGINA INICIAL E BUSCA (HTMX) ---
@app.route('/')
def index():
    busca = request.args.get('bairro')
    resultados = []
    
    # Variável para guardar o nome oficial (com acento) para mostrar na tela depois
    nome_oficial = busca 

    if busca:
        # 1. Tira os acentos e deixa minúsculo o que o usuário digitou
        busca_limpa = unicodedata.normalize('NFKD', busca).encode('ASCII', 'ignore').decode('utf-8').lower().strip()

        conn = sqlite3.connect('coleta.db')
        cursor = conn.cursor()
        
        # Puxamos todos os horários e nomes dos bairros do banco
        cursor.execute('''
            SELECT c.tipo_lixo, c.dia_semana, c.horario, b.nome
            FROM cronograma c
            JOIN bairros b ON c.bairro_id = b.id
        ''')
        
        # 2. Filtramos no próprio Python (que é muito mais inteligente que o SQLite para textos)
        for linha in cursor.fetchall():
            nome_banco = linha[3] # O nome do bairro que veio do banco
            
            # Tira os acentos e deixa minúsculo o nome que está no banco de dados
            nome_banco_limpo = unicodedata.normalize('NFKD', nome_banco).encode('ASCII', 'ignore').decode('utf-8').lower()
            
            # Compara as duas versões "limpas"
            if busca_limpa in nome_banco_limpo:
                # Se achou, guarda os horários e salva o nome oficial com acento
                resultados.append((linha[0], linha[1], linha[2]))
                nome_oficial = nome_banco 
        
        conn.close()

        # Se a requisição veio do HTMX, devolvemos o HTML
        if 'HX-Request' in request.headers:
            return render_template('resultados.html', resultados=resultados, busca=nome_oficial)

    # Se for um acesso normal, devolve a página inteira
    return render_template('index.html')

# --- ROTA 2: GUIA DE DESCARTE ---
@app.route('/guia')
def guia():
    return render_template('guia.html')

# --- ROTA 3: ASSISTENTE VIRTUAL COM IA ---
@app.route('/perguntar-ia')
def assistente_ia():
    pergunta_usuario = request.args.get('duvida','')[:500]
    
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


@app.route('/contatos')
def contatos():
    return render_template('contatos.html')


# --- INICIALIZAÇÃO DO SERVIDOR ---
if __name__ == '__main__':
    init_db() # Garante que o banco exista sempre que o código rodar
    print("Servidor rodando! Acesse: http://127.0.0.1:5000")
    app.run(debug=True)
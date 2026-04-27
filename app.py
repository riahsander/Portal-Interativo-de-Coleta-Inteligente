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
    # GRUPO 1: Seletiva (Ter e Sáb) | Orgânica (Seg, Qua e Sex)
    'Z Industrial Norte': ('Terça e Sábado', 'Quarta e Sexta'), # Exceção: Sem orgânica à Seg
    'Z Rural Norte': ('Terça e Sábado', 'Quarta e Sexta'),      # Exceção: Sem orgânica à Seg
    'Alto Paulista': ('Terça e Sábado', 'Segunda, Quarta e Sexta'),
    'Aurora': ('Terça e Sábado', 'Segunda, Quarta e Sexta'),
    'Celeste': ('Terça e Sábado', 'Segunda, Quarta e Sexta'),
    'Colina Deuner': ('Terça e Sábado', 'Segunda, Quarta e Sexta'),
    'Dona Augusta': ('Terça e Sábado', 'Segunda, Quarta e Sexta'),
    'Firenze': ('Terça e Sábado', 'Segunda, Quarta e Sexta'),
    'Genuíno Sampaio': ('Terça e Sábado', 'Segunda, Quarta e Sexta'),
    'Imigrante Norte': ('Terça e Sábado', 'Segunda, Quarta e Sexta'),
    'Imigrante Sul': ('Terça e Sábado', 'Segunda, Quarta e Sexta'),
    'Ipiranga': ('Terça e Sábado', 'Segunda, Quarta e Sexta'),
    'Metzler': ('Terça e Sábado', 'Segunda, Quarta e Sexta'),
    'Paulista': ('Terça e Sábado', 'Segunda, Quarta e Sexta'),
    'Rio Branco': ('Terça e Sábado', 'Segunda, Quarta e Sexta'),
    'Solar do Campo': ('Terça e Sábado', 'Segunda, Quarta e Sexta'),
    
    # ATENÇÃO: Define aqui qual é o esquema correto para o Centro
    'Centro': ('Terça e Sábado', 'Segunda, Quarta e Sexta'), 

    # GRUPO 2: Seletiva (Seg e Sex) | Orgânica (Ter e Qui)
    'Z Industrial Sul': ('Segunda e Sexta', 'Terça e Quinta'),
    'Zona Rural Sul': ('Segunda e Sexta', 'Terça e Quinta'),

    # GRUPO 3: Seletiva (Seg e Sex) | Orgânica (Ter, Qui e Sáb)
    '25 de Julho': ('Segunda e Sexta', 'Terça, Quinta e Sábado'),
    'Barrinha': ('Segunda e Sexta', 'Terça, Quinta e Sábado'),
    'Bela Vista': ('Segunda e Sexta', 'Terça, Quinta e Sábado'),
    'Bem Viver': ('Segunda e Sexta', 'Terça, Quinta e Sábado'),
    'Cohab Leste': ('Segunda e Sexta', 'Terça, Quinta e Sábado'),
    'Cohab Sul': ('Segunda e Sexta', 'Terça, Quinta e Sábado'),
    'Esperança': ('Segunda e Sexta', 'Terça, Quinta e Sábado'),
    'Floresta': ('Segunda e Sexta', 'Terça, Quinta e Sábado'),
    'Gringos': ('Segunda e Sexta', 'Terça, Quinta e Sábado'),
    'Jardim do Sol': ('Segunda e Sexta', 'Terça, Quinta e Sábado'),
    'Mônaco': ('Segunda e Sexta', 'Terça, Quinta e Sábado'),
    'Operária': ('Segunda e Sexta', 'Terça, Quinta e Sábado'),
    'Porto Blos': ('Segunda e Sexta', 'Terça, Quinta e Sábado'),
    'Quatro Colônias': ('Segunda e Sexta', 'Terça, Quinta e Sábado'),
    'Santa Lucia': ('Segunda e Sexta', 'Terça, Quinta e Sábado'),
    'Santo Antônio': ('Segunda e Sexta', 'Terça, Quinta e Sábado'),
    'Sempre Unidos': ('Segunda e Sexta', 'Terça, Quinta e Sábado'),
    'Vila Brito': ('Segunda e Sexta', 'Terça, Quinta e Sábado'),
    'Vila Nova': ('Segunda e Sexta', 'Terça, Quinta e Sábado'),
    'Vila Reicher': ('Segunda e Sexta', 'Terça, Quinta e Sábado'),
    'Vila Rica': ('Segunda e Sexta', 'Terça, Quinta e Sábado')
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
import sqlite3

def popular_banco_completo():
    conn = sqlite3.connect('coleta.db')
    cursor = conn.cursor()

    # Dicionário com todos os bairros: Nome -> (Dia do Lixo Seco, Dias do Lixo Orgânico)
    dados_bairros = {
        # Segunda-feira
        'Cohab Sul': ('Segunda-feira', 'Terça e Quinta-feira'),
        'Centro': ('Segunda-feira', 'Terça e Quinta-feira'),
        'Bela Vista': ('Segunda-feira', 'Terça e Quinta-feira'),
        '25 de Julho': ('Segunda-feira', 'Terça e Quinta-feira'),
        'Colina Deuner': ('Segunda-feira', 'Terça e Quinta-feira'),
        'Cohab Leste': ('Segunda-feira', 'Terça e Quinta-feira'),
        'Jardim do Sol': ('Segunda-feira', 'Terça e Quinta-feira'),
        'Barrinha': ('Segunda-feira', 'Terça e Quinta-feira'),
        
        # Terça-feira
        'Firenze': ('Terça-feira', 'Quarta e Sexta-feira'),
        'Metzler': ('Terça-feira', 'Quarta e Sexta-feira'),
        'Renascer': ('Terça-feira', 'Quarta e Sexta-feira'),
        'Aurora': ('Terça-feira', 'Quarta e Sexta-feira'),
        'Rio Branco': ('Terça-feira', 'Quarta e Sexta-feira'),
        
        # Quarta-feira
        'Operária': ('Quarta-feira', 'Terça e Quinta-feira'),
        'Sempre Unidos': ('Quarta-feira', 'Terça e Quinta-feira'),
        'Esperança': ('Quarta-feira', 'Terça e Quinta-feira'),
        'Floresta': ('Quarta-feira', 'Terça e Quinta-feira'),
        'Industrial Sul': ('Quarta-feira', 'Terça e Quinta-feira'),
        'Bem Viver I': ('Quarta-feira', 'Terça e Quinta-feira'),
        'Bem Viver II': ('Quarta-feira', 'Terça e Quinta-feira'),
        'Gringos': ('Quarta-feira', 'Terça e Quinta-feira'),
        'Vila Rica': ('Quarta-feira', 'Terça e Quinta-feira'),
        'Porto Blos': ('Quarta-feira', 'Terça e Quinta-feira'),
        'Celeste': ('Quinta-feira', 'Terça, Quintas e Sábados'),
        
        # Sexta-feira
        'Quatro Colônias': ('Sexta-feira', 'Terça e Quinta-feira'),
        'Santa Lúcia': ('Sexta-feira', 'Terça e Quinta-feira'),
        'Santo Antônio': ('Sexta-feira', 'Terça e Quinta-feira'),
        'Bem Viver III': ('Sexta-feira', 'Terça e Quinta-feira'),
        'Morada do Sol': ('Sexta-feira', 'Terça e Quinta-feira'),
        'União': ('Sexta-feira', 'Terça e Quinta-feira'),
        
        # Sábado
        'Alto Paulista': ('Sábado', 'Segunda e Quarta-feira'),
        'Paulista': ('Sábado', 'Segunda e Quarta-feira'),
        'Solar do Campo': ('Sábado', 'Segunda e Quarta-feira'),
        'Recanto da Paz': ('Sábado', 'Segunda e Quarta-feira'),
        'Zona Industrial Norte': ('Sábado', 'Quartas e Sextas-feira'),
        'Zona Rural Norte': ('Sábado', 'Quartas e Sextas-feira'),
        'Zona Expansão Urbana Leste': ('Sábado', 'Segunda e Quarta-feira')
    }

    # 1. Inserir todos os bairros na tabela 'bairros'
    for bairro in dados_bairros.keys():
        try:
            cursor.execute('INSERT INTO bairros (nome) VALUES (?)', (bairro,))
        except sqlite3.IntegrityError:
            pass # Ignora se o bairro já estiver salvo no banco

    # 2. Pegar os IDs gerados pelo banco para cada bairro
    cursor.execute('SELECT id, nome FROM bairros')
    bairros_db = {nome: id for id, nome in cursor.fetchall()}

    # 3. Limpar o cronograma antigo (para não duplicar os testes que fizemos)
    cursor.execute('DELETE FROM cronograma')

    # 4. Inserir os horários completos para a cidade inteira
    for bairro, horarios in dados_bairros.items():
        id_bairro = bairros_db[bairro]
        dia_seco = horarios[0]
        dias_organico = horarios[1]

        # Adiciona o Lixo Seco
        cursor.execute(
            'INSERT INTO cronograma (bairro_id, tipo_lixo, dia_semana) VALUES (?, ?, ?)',
            (id_bairro, 'Lixo Seco (Reciclável)', dia_seco)
        )
        # Adiciona o Lixo Orgânico
        cursor.execute(
            'INSERT INTO cronograma (bairro_id, tipo_lixo, dia_semana) VALUES (?, ?, ?)',
            (id_bairro, 'Lixo Orgânico / Comum', dias_organico)
        )

    conn.commit()
    conn.close()
    print("✅ Banco de dados atualizado! Todos os bairros de Campo Bom foram adicionados.")

if __name__ == '__main__':
    popular_banco_completo()
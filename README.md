# ♻️ Portal Interativo de Coleta Inteligente - Campo Bom

Este é um projeto de extensão focado em sustentabilidade e cidades inteligentes, desenvolvido para facilitar o acesso à informação sobre o recolhimento de resíduos na cidade de Campo Bom (RS).

A aplicação permite que os moradores consultem rapidamente os dias de coleta (Lixo Seco e Orgânico) em seus bairros e utilizem um assistente virtual baseado em Inteligência Artificial para descobrir onde descartar materiais específicos (como eletrônicos, pilhas e entulhos).

## 🚀 Funcionalidades Principais

* **Busca Inteligente de Bairros:** Mapeamento completo de todos os 49 bairros oficiais, zonas rurais e loteamentos da cidade. O sistema possui busca tolerante a erros de digitação, ignorando acentos e letras maiúsculas/minúsculas.
* **Assistente de Descarte (IA):** Integração com a API da Groq (modelos Llama 3 da Meta) para responder dúvidas reais dos usuários sobre as regras de descarte específicas do município (CEMEA, Caco Treco, etc).
* **Banco de Dados Resiliente:** Arquitetura adaptada para deploy gratuito na nuvem (Discos Efêmeros). O sistema detecta automaticamente se o banco SQLite está vazio e se auto-popula com os dados oficiais da prefeitura ao iniciar o servidor.
* **Interface Dinâmica:** Utilização de HTMX para requisições assíncronas, garantindo uma experiência fluida para o usuário sem a necessidade de recarregar a página.

## 🛠️ Tecnologias Utilizadas

* **Backend:** Python, Flask, Gunicorn
* **Banco de Dados:** SQLite3
* **Inteligência Artificial:** Groq API (Llama 3.3 70B / Llama 3.1 8B)
* **Frontend:** HTML5, CSS3, HTMX
* **Deploy e Nuvem:** Render (Web Services)

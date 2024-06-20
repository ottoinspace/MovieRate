# MovieRate

## Descrição

MovieRate é uma aplicação web desenvolvida com FastAPI que permite aos usuários gerenciar uma lista de filmes. A aplicação utiliza OAuth para autenticação e SQLite como banco de dados.

## Pré-requisitos

- Python 3.11
- [Poetry](https://python-poetry.org/docs/#installation) (para gerenciamento de dependências)

## Instalação

1. **Clone o repositório:**

   ```bash
   git clone https://github.com/seu-usuario/movierate.git
   cd movierate

2. **Instale as dependências com Poetry:**
   
   ```bash
   poetry install

4. **Configure as variáveis de ambiente:**

  Crie um arquivo .env na raiz do projeto e adicione as seguintes variáveis (substitua pelos valores reais):

  ```env 
  DOMAIN=your-auth0-domain
  CLIENT_ID=your-auth0-client-id
  CLIENT_SECRET=your-auth0-client-secret
  SECRET_KEY=your-secret-key
  ```
## Como Executar

1. **Inicie uma shell do Poetry:**

   ```bash
   poetry shell
   ```
2. **Execute a aplicação com Uvicorn:**

   ```bash
   uvicorn movierate.app:app

3. **Acesse a aplicação:**

   Abra seu navegador e vá para http://localhost:8000.

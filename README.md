# Planos de Ano Novo

Aplicativo Streamlit para definir e acompanhar objetivos e metas ao longo do ano, com autenticação via Google e armazenamento local em SQLite.

## Recursos planejados
- Autenticação com Google OAuth 2.0
- Cadastro de objetivos e metas mensuráveis (SMART)
- Dashboard com indicadores consolidados e gráfico de progresso
- Revisões mensais com exportação dos dados em Excel

## Pré-requisitos
- Python 3.11+
- Conta Google para configuração do OAuth

## Configuração inicial
1. Crie um arquivo `.streamlit/secrets.toml` com as credenciais do Google e URL do banco (veja comentários no arquivo de exemplo já criado).
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Execute a aplicação:
   ```bash
   streamlit run app/main.py
   ```

## Estrutura de pastas
- `app/` contém o código principal da aplicação
  - `auth/` utilitários de autenticação
  - `data/` configuração do banco e modelos SQLAlchemy
  - `pages/` páginas multipágina do Streamlit
  - `ui/` componentes de interface reutilizáveis
- `.streamlit/` configurações e segredos da aplicação

## Próximos passos
- Implementar persistência completa das revisões mensais
- Integrar fluxo completo de OAuth (armazenar usuário no banco)
- Adicionar testes automatizados para camadas de dados

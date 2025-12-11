# CredMiner HB - Sistema de Recuperação de Crédito

Sistema completo de gestão de cobranças judiciais com cálculo automático de correção monetária e juros.

##  Acesso ao Sistema

**URL de Acesso:** https://credminerhb.streamlit.app

**Credenciais padrão:**
- **Usuário:** admin
- **Senha:** admin

 **IMPORTANTE:** Altere a senha padrão após o primeiro acesso!

##  Funcionalidades

-  Cadastro completo de devedores, endereços e fiadores
-  Gestão de dívidas por tipo de contrato (CESU, PAFE, PPD, Mensalidades, Judicial)
-  Cálculo automático de correção monetária (INPC, IPC-FIPE, IPCA)
-  Inclusão de custas judiciais
-  Simulação de acordos e negociações
-  Sistema de autenticação com múltiplos usuários
-  Links compartilháveis para acesso

##  Tecnologias

- **Backend:** Python + Streamlit
- **Banco de Dados:** SQLite (local) ou PostgreSQL/Supabase (produção)
- **Scraping:** BeautifulSoup4 para atualização de índices AASP
- **Autenticação:** bcrypt

##  Instalação Local

```bash
# Clone o repositório
git clone https://github.com/RMSuyama/credminerhb.git
cd credminerhb

# Instale as dependências
pip install -r requirements.txt

# Execute o aplicativo
streamlit run app.py
```

##  Configuração do Banco de Dados

### SQLite (Padrão)
Por padrão, o sistema usa SQLite e não requer configuração adicional.

### PostgreSQL/Supabase (Opcional)
Para usar PostgreSQL (recomendado para produção):

1. Copie `.env.example` para `.env`
2. Configure as variáveis:
```env
USE_SUPABASE=true
SUPABASE_HOST=seu-projeto.supabase.co
SUPABASE_PORT=5432
SUPABASE_DB=postgres
SUPABASE_USER=postgres
SUPABASE_PASSWORD=sua-senha
```

##  Gerenciamento de Usuários

Acesse **Configurações** no menu lateral para:
- Criar novos usuários
- Gerar links de acesso compartilháveis
- Atualizar índices econômicos

##  Tipos de Contrato

O sistema suporta cálculos específicos para:

- **CESU:** Correção INPC + Juros 1% a.m. (pro-rata) + Multa 2%
- **PAFE:** Correção IPC-FIPE + Juros 1% a.m. (pro-rata) + Multa 2%
- **PPD:** Correção IPCA + Juros 1% a.m. (sem pro-rata) + Multa 20%
- **MENSALIDADES:** Correção IPCA + Multa configurável (2% ou 20%)
- **JUDICIAL:** Correção IPCA + Juros 1% a.m.

##  Atualização de Índices

O sistema pode buscar automaticamente os índices econômicos do site da AASP:
1. Acesse **Configurações** no menu
2. Clique em **Atualizar Índices (SELIC/IPCA)**

##  Contribuições

Desenvolvido por RMSuyama

##  Licença

Este projeto é proprietário. Todos os direitos reservados.

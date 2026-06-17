# 🎫 TicketFlow

Sistema de gerenciamento de chamados internos (Help Desk) desenvolvido em Python, com persistência em PostgreSQL e interface gráfica em Tkinter.

Permite abrir, listar, filtrar, atualizar e encerrar chamados de diferentes departamentos (TI, RH, Financeiro e Infraestrutura), cada um com seus próprios campos específicos.

## Índice

- [Tecnologias](#tecnologias)
- [Conceitos aplicados](#conceitos-aplicados)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Como rodar](#como-rodar)
- [Funcionalidades](#funcionalidades)
- [Possíveis melhorias futuras](#possíveis-melhorias-futuras)

## Tecnologias

- Python 3.12+
- PostgreSQL
- psycopg2
- Tkinter (interface gráfica nativa)

## Conceitos aplicados

- Programação Orientada a Objetos
- Classes Abstratas (`Chamado`)
- Herança (`ChamadoTI`, `ChamadoRH`, `ChamadoFinanceiro`, `ChamadoInfraestrutura`)
- Polimorfismo e Override (`exibir_detalhes()`)
- Encapsulamento (atributos privados com properties)
- Exceções personalizadas (`ChamadoInvalidoException`)
- Arquitetura em camadas (models / dao / services)
- CRUD completo com PostgreSQL

## Estrutura do projeto

```
ticketflow/
├── main.py                          # Interface gráfica (Tkinter)
├── config.ini.example               # Modelo de configuração
├── requirements.txt
├── sql/
│   └── setup.sql                    # Banco + tabelas + dados iniciais
├── database/
│   └── connection.py                # Singleton de conexão
├── exceptions/
│   └── chamado_invalido_exception.py
├── models/
│   ├── chamado.py                   # Classe abstrata
│   ├── chamado_ti.py
│   ├── chamado_rh.py
│   ├── chamado_financeiro.py
│   ├── chamado_infraestrutura.py
│   └── usuario.py
├── dao/
│   ├── chamado_dao.py
│   └── usuario_dao.py
└── services/
    └── chamado_service.py
```

## Como rodar

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar o PostgreSQL

Execute os comandos abaixo no terminal com o usuário `postgres`:

```bash
psql -U postgres -c "CREATE DATABASE ticketflow ENCODING 'UTF8';"
psql -U postgres -c "CREATE USER ticketflow WITH PASSWORD '1234';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE ticketflow TO ticketflow;"
psql -U postgres -d ticketflow -f sql/setup.sql
```

### 3. Configurar a conexão

Copie o arquivo de exemplo:

```bash
cp config.ini.example config.ini
```

O arquivo já vem com as credenciais padrão do projeto:

| Campo    | Valor       |
|----------|-------------|
| Host     | localhost   |
| Porta    | **5432**    |
| Banco    | ticketflow  |
| Usuário  | ticketflow  |
| Senha    | **1234**    |

> O arquivo `config.ini` está no `.gitignore` e não é enviado ao repositório.
> Na primeira conexão bem-sucedida, as credenciais são salvas automaticamente — nas próximas execuções o sistema abre direto, sem pedir senha.

### 4. Executar

```bash
cd ticketflow
python main.py
```

Na tela inicial, informe a senha de acesso ao sistema (**1234**) para liberar a conexão.

## Funcionalidades

- Abertura de chamados por tipo: TI, RH, Financeiro, Infraestrutura
- Listagem com filtros por status, prioridade, departamento e ID
- Visualização detalhada (duplo clique na linha)
- Atualização de título, descrição, prioridade e status
- Encerramento e exclusão de chamados
- Relatórios: por departamento, status, prioridade e resumo geral
- Cores na tabela: vermelho (Crítica), laranja (Alta), cinza (Encerrado)

## Possíveis melhorias futuras

- Autenticação de usuários com perfis de acesso (solicitante / atendente / admin)
- Histórico de alterações por chamado
- Exportação de relatórios para CSV/PDF
- Testes automatizados (unitários e de integração)

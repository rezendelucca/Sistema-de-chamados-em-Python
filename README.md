# TicketFlow
# 🎫 TicketFlow

Sistema de gerenciamento de chamados internos (Help Desk) desenvolvido em Python com PostgreSQL e inter
face gráfica em Tkinter.
Sistema de gerenciamento de chamados internos (Help Desk) desenvolvido em Python, com persistência em P
ostgreSQL e interface gráfica em Tkinter.

Permite abrir, listar, filtrar, atualizar e encerrar chamados de diferentes departamentos (TI, RH, Fina
nceiro e Infraestrutura), cada um com seus próprios campos específicos.

● Write(README.md)
Added 24 lines, removed 4 lines
# TicketFlow
# 🎫 TicketFlow

 e encerrar chamados de diferentes departamentos (TI, RH, Fina
nceiro e Infraestrutura), cada um com seus próprios campos específicos.

## Índice

- [Tecnologias](#tecnologias)
- [Conceitos aplicados](#conceitos-aplicados)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Como rodar](#como-rodar)
- [Funcionalidades](#funcionalidades
- [Possíveis melhorias futuras](#possíveis-melhorias-futuras)

## Tecnologias


pip install -r requirements.txt
```

### 2. Configurar o PostgreSQL

| Usuário  | ticketflow  |
| Senha    | **1234**    |

> O arquivo `config.ini` está no `.gitignore` e não é enviado ao repositório.
> O arquivo `config.ini` está no `.gitignore` e não é enviado ao repositório.
> Na primeira conexão bem-sucedida, as credenciais são salvas automaticamente — nas próximas execuções
 o sistema abre direto, sem pedir s

python main.py
```

Na tela inicial, informe a senha de acesso ao sistema (**1234**) para liberar a conexão.

## Funcionalidades

- Abertura de chamados por tipo: TIura

- Encerramento e exclusão de chamad
- Relatórios: por departamento, status, prioridade e resumo geral
- Cores na tabela: vermelho (Crítica), laranja (Alta), cinza (Encerrado)

## Possíveis melhorias futuras

- Autenticação de usuários com perftendente / admin)
- Histórico de alterações por chamado
- Exportação de relatórios para CSV/PDF
- Testes automatizados (unitários e

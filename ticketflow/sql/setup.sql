-- =============================================================
--  TicketFlow - Script de configuracao do banco de dados
--  Executar em duas etapas:
--    1. Passo 1 como superusuario no psql (cria o banco)
--    2. Passo 2 conectado ao banco ticketflow
-- =============================================================


-- =============================================================
--  PASSO 1: Executar como superusuario
--    psql -U postgres -c "CREATE DATABASE ticketflow ENCODING 'UTF8';"
--  Ou descomente as linhas abaixo:
-- =============================================================
-- DROP DATABASE IF EXISTS ticketflow;
-- CREATE DATABASE ticketflow ENCODING 'UTF8';

-- =============================================================
--  USUARIO DEDICADO DO SISTEMA
--  Execute como superusuario antes de rodar este script:
--    psql -U postgres -c "CREATE USER ticketflow WITH PASSWORD '1234';"
--    psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE ticketflow TO ticketflow;"
-- =============================================================


-- =============================================================
--  PASSO 2: Conectar ao banco e executar o restante
--    psql -U postgres -d ticketflow -f setup.sql
-- =============================================================


-- -------------------------------------------------------------
--  TABELA: usuario
-- -------------------------------------------------------------
DROP TABLE IF EXISTS chamado;
DROP TABLE IF EXISTS usuario;

CREATE TABLE usuario (
    id           SERIAL       PRIMARY KEY,
    nome         VARCHAR(100) NOT NULL,
    email        VARCHAR(150) NOT NULL UNIQUE,
    departamento VARCHAR(100) NOT NULL
);


-- -------------------------------------------------------------
--  TABELA: chamado
-- -------------------------------------------------------------
CREATE TABLE chamado (
    id               SERIAL       PRIMARY KEY,
    titulo           VARCHAR(200) NOT NULL,
    descricao        TEXT         NOT NULL,
    tipo             VARCHAR(20)  NOT NULL
                         CHECK (tipo IN ('TI','RH','FINANCEIRO','INFRAESTRUTURA')),
    prioridade       VARCHAR(20)  NOT NULL
                         CHECK (prioridade IN ('BAIXA','MEDIA','ALTA','CRITICA')),
    status           VARCHAR(20)  NOT NULL DEFAULT 'ABERTO'
                         CHECK (status IN ('ABERTO','EM_ANDAMENTO','ENCERRADO','CANCELADO')),
    data_abertura    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    usuario_id       INTEGER      NOT NULL REFERENCES usuario(id) ON DELETE RESTRICT,

    -- campos especificos de cada subclasse
    categoria_ti     VARCHAR(100),   -- ChamadoTI
    cargo_afetado    VARCHAR(100),   -- ChamadoRH
    centro_custo     VARCHAR(100),   -- ChamadoFinanceiro
    local_instalacao VARCHAR(100)    -- ChamadoInfraestrutura
);

-- Indices para as buscas mais comuns
CREATE INDEX idx_chamado_status     ON chamado(status);
CREATE INDEX idx_chamado_prioridade ON chamado(prioridade);
CREATE INDEX idx_chamado_tipo       ON chamado(tipo);
CREATE INDEX idx_chamado_usuario    ON chamado(usuario_id);


-- -------------------------------------------------------------
--  DADOS INICIAIS: usuarios
-- -------------------------------------------------------------
INSERT INTO usuario (nome, email, departamento) VALUES
    ('Ana Silva',       'ana.silva@empresa.com',       'TI'),
    ('Bruno Costa',     'bruno.costa@empresa.com',     'RH'),
    ('Carla Mendes',    'carla.mendes@empresa.com',    'Financeiro'),
    ('Diego Oliveira',  'diego.oliveira@empresa.com',  'Infraestrutura'),
    ('Eduarda Lima',    'eduarda.lima@empresa.com',    'Comercial'),
    ('Felipe Santos',   'felipe.santos@empresa.com',   'TI'),
    ('Gabriela Rocha',  'gabriela.rocha@empresa.com',  'RH'),
    ('Henrique Souza',  'henrique.souza@empresa.com',  'Financeiro');


-- -------------------------------------------------------------
--  DADOS INICIAIS: chamados de exemplo
-- -------------------------------------------------------------
INSERT INTO chamado (titulo, descricao, tipo, prioridade, status, usuario_id, categoria_ti)
VALUES ('Computador nao liga',
        'Ao pressionar o botao power, o computador nao responde.',
        'TI', 'ALTA', 'ABERTO', 1, 'Hardware');

INSERT INTO chamado (titulo, descricao, tipo, prioridade, status, usuario_id, cargo_afetado)
VALUES ('Atualizacao de contrato',
        'Necessario atualizar dados contratuais do funcionario.',
        'RH', 'MEDIA', 'EM_ANDAMENTO', 2, 'Analista');

INSERT INTO chamado (titulo, descricao, tipo, prioridade, status, usuario_id, centro_custo)
VALUES ('Reembolso de despesas',
        'Solicitacao de reembolso referente a viagem corporativa de maio.',
        'FINANCEIRO', 'BAIXA', 'ABERTO', 3, 'CC-001');

INSERT INTO chamado (titulo, descricao, tipo, prioridade, status, usuario_id, local_instalacao)
VALUES ('Ar condicionado com defeito',
        'O ar condicionado da sala 302 esta apresentando falhas de resfriamento.',
        'INFRAESTRUTURA', 'ALTA', 'ABERTO', 4, 'Sala 302');

INSERT INTO chamado (titulo, descricao, tipo, prioridade, status, usuario_id, categoria_ti)
VALUES ('Acesso ao sistema ERP',
        'Solicito acesso ao modulo financeiro do sistema ERP.',
        'TI', 'MEDIA', 'ENCERRADO', 5, 'Software');

INSERT INTO chamado (titulo, descricao, tipo, prioridade, status, usuario_id, cargo_afetado)
VALUES ('Inclusao em plano de saude',
        'Solicito inclusao de dependente no plano de saude corporativo.',
        'RH', 'BAIXA', 'ABERTO', 6, 'Estagiario');

INSERT INTO chamado (titulo, descricao, tipo, prioridade, status, usuario_id, centro_custo)
VALUES ('Aprovacao de orcamento urgente',
        'Orcamento para compra de notebooks pendente de aprovacao da diretoria.',
        'FINANCEIRO', 'CRITICA', 'EM_ANDAMENTO', 7, 'CC-002');

INSERT INTO chamado (titulo, descricao, tipo, prioridade, status, usuario_id, local_instalacao)
VALUES ('Instalacao de ponto de rede',
        'Necessario instalar novo ponto de rede na sala de reunioes do 2o andar.',
        'INFRAESTRUTURA', 'MEDIA', 'ABERTO', 8, 'Sala de Reunioes - 2o Andar');


-- Permissoes para o usuario ticketflow
GRANT ALL ON ALL TABLES    IN SCHEMA public TO ticketflow;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO ticketflow;

-- Verificacao final
SELECT 'Usuarios cadastrados: ' || COUNT(*) FROM usuario;
SELECT 'Chamados cadastrados: ' || COUNT(*) FROM chamado;

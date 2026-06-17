from typing import List, Optional

from database.connection import DatabaseConnection
from models.chamado import Chamado
from models.chamado_financeiro import ChamadoFinanceiro
from models.chamado_infraestrutura import ChamadoInfraestrutura
from models.chamado_rh import ChamadoRH
from models.chamado_ti import ChamadoTI
from models.usuario import Usuario


_TIPO_CLASSE = {
    'TI': ChamadoTI,
    'RH': ChamadoRH,
    'FINANCEIRO': ChamadoFinanceiro,
    'INFRAESTRUTURA': ChamadoInfraestrutura,
}

_CLASSE_TIPO = {v.__name__: k for k, v in _TIPO_CLASSE.items()}


class ChamadoDAO:
    def __init__(self):
        self._db = DatabaseConnection.get_instance()

    # Retorna o tipo string a partir da instancia do chamado
    @staticmethod
    def tipo_de(chamado: Chamado) -> str:
        return _CLASSE_TIPO.get(type(chamado).__name__, 'TI')

    def _mapear(self, row) -> Chamado:
        usuario = Usuario(
            row['usuario_id'],
            row['usuario_nome'],
            row['usuario_email'],
            row['usuario_departamento']
        )
        tipo = row['tipo']
        Classe = _TIPO_CLASSE[tipo]
        kwargs = dict(
            id=row['id'],
            titulo=row['titulo'],
            descricao=row['descricao'],
            prioridade=row['prioridade'],
            status=row['status'],
            usuario=usuario,
            data_abertura=row['data_abertura'],
        )
        if tipo == 'TI':
            kwargs['categoria_ti'] = row.get('categoria_ti')
        elif tipo == 'RH':
            kwargs['cargo_afetado'] = row.get('cargo_afetado')
        elif tipo == 'FINANCEIRO':
            kwargs['centro_custo'] = row.get('centro_custo')
        elif tipo == 'INFRAESTRUTURA':
            kwargs['local_instalacao'] = row.get('local_instalacao')
        return Classe(**kwargs)

    def _query_base(self) -> str:
        return """
            SELECT
                c.*,
                u.nome        AS usuario_nome,
                u.email       AS usuario_email,
                u.departamento AS usuario_departamento
            FROM chamado c
            JOIN usuario u ON c.usuario_id = u.id
        """

    def _campos_especificos(self, chamado: Chamado):
        return (
            getattr(chamado, 'categoria_ti',     None),
            getattr(chamado, 'cargo_afetado',    None),
            getattr(chamado, 'centro_custo',     None),
            getattr(chamado, 'local_instalacao', None),
        )

    def criar(self, chamado: Chamado) -> Chamado:
        tipo = self.tipo_de(chamado)
        cat_ti, cargo, custo, local = self._campos_especificos(chamado)
        cursor = self._db.get_cursor()
        cursor.execute(
            """
            INSERT INTO chamado
                (titulo, descricao, tipo, prioridade, status, usuario_id,
                 categoria_ti, cargo_afetado, centro_custo, local_instalacao)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, data_abertura
            """,
            (
                chamado.titulo, chamado.descricao, tipo,
                chamado.prioridade, chamado.status, chamado.usuario.id,
                cat_ti, cargo, custo, local,
            )
        )
        resultado = cursor.fetchone()
        self._db.commit()
        chamado.id = resultado['id']
        chamado.data_abertura = resultado['data_abertura']
        return chamado

    def buscar_por_id(self, id: int) -> Optional[Chamado]:
        cursor = self._db.get_cursor()
        cursor.execute(self._query_base() + "WHERE c.id = %s", (id,))
        row = cursor.fetchone()
        return self._mapear(row) if row else None

    def listar_todos(self) -> List[Chamado]:
        cursor = self._db.get_cursor()
        cursor.execute(self._query_base() + "ORDER BY c.data_abertura DESC")
        return [self._mapear(r) for r in cursor.fetchall()]

    def buscar_por_status(self, status: str) -> List[Chamado]:
        cursor = self._db.get_cursor()
        cursor.execute(
            self._query_base() + "WHERE c.status = %s ORDER BY c.data_abertura DESC",
            (status.upper(),)
        )
        return [self._mapear(r) for r in cursor.fetchall()]

    def buscar_por_prioridade(self, prioridade: str) -> List[Chamado]:
        cursor = self._db.get_cursor()
        cursor.execute(
            self._query_base() + "WHERE c.prioridade = %s ORDER BY c.data_abertura DESC",
            (prioridade.upper(),)
        )
        return [self._mapear(r) for r in cursor.fetchall()]

    def buscar_por_usuario(self, usuario_id: int) -> List[Chamado]:
        cursor = self._db.get_cursor()
        cursor.execute(
            self._query_base() + "WHERE c.usuario_id = %s ORDER BY c.data_abertura DESC",
            (usuario_id,)
        )
        return [self._mapear(r) for r in cursor.fetchall()]

    def buscar_por_departamento(self, departamento: str) -> List[Chamado]:
        cursor = self._db.get_cursor()
        cursor.execute(
            self._query_base() + "WHERE u.departamento ILIKE %s ORDER BY c.data_abertura DESC",
            (f'%{departamento}%',)
        )
        return [self._mapear(r) for r in cursor.fetchall()]

    def atualizar(self, chamado: Chamado) -> bool:
        cat_ti, cargo, custo, local = self._campos_especificos(chamado)
        cursor = self._db.get_cursor()
        cursor.execute(
            """
            UPDATE chamado
            SET titulo           = %s,
                descricao        = %s,
                prioridade       = %s,
                status           = %s,
                categoria_ti     = %s,
                cargo_afetado    = %s,
                centro_custo     = %s,
                local_instalacao = %s
            WHERE id = %s
            """,
            (
                chamado.titulo, chamado.descricao,
                chamado.prioridade, chamado.status,
                cat_ti, cargo, custo, local,
                chamado.id,
            )
        )
        self._db.commit()
        return cursor.rowcount > 0

    def encerrar(self, id: int) -> bool:
        cursor = self._db.get_cursor()
        cursor.execute("UPDATE chamado SET status = 'ENCERRADO' WHERE id = %s", (id,))
        self._db.commit()
        return cursor.rowcount > 0

    def excluir(self, id: int) -> bool:
        cursor = self._db.get_cursor()
        cursor.execute("DELETE FROM chamado WHERE id = %s", (id,))
        self._db.commit()
        return cursor.rowcount > 0

    # --- Relatorios ---

    def relatorio_por_departamento(self) -> list:
        cursor = self._db.get_cursor()
        cursor.execute("""
            SELECT u.departamento, COUNT(c.id) AS total
            FROM chamado c
            JOIN usuario u ON c.usuario_id = u.id
            GROUP BY u.departamento
            ORDER BY total DESC
        """)
        return cursor.fetchall()

    def relatorio_por_status(self) -> list:
        cursor = self._db.get_cursor()
        cursor.execute("""
            SELECT status, COUNT(*) AS total
            FROM chamado
            GROUP BY status
            ORDER BY total DESC
        """)
        return cursor.fetchall()

    def relatorio_por_prioridade(self) -> list:
        cursor = self._db.get_cursor()
        cursor.execute("""
            SELECT prioridade, COUNT(*) AS total
            FROM chamado
            GROUP BY prioridade
            ORDER BY total DESC
        """)
        return cursor.fetchall()

    def relatorio_resumo(self) -> dict:
        cursor = self._db.get_cursor()
        cursor.execute("""
            SELECT
                SUM(CASE WHEN status = 'ABERTO'       THEN 1 ELSE 0 END) AS abertos,
                SUM(CASE WHEN status = 'EM_ANDAMENTO' THEN 1 ELSE 0 END) AS em_andamento,
                SUM(CASE WHEN status = 'ENCERRADO'    THEN 1 ELSE 0 END) AS encerrados,
                SUM(CASE WHEN status = 'CANCELADO'    THEN 1 ELSE 0 END) AS cancelados
            FROM chamado
        """)
        return cursor.fetchone()

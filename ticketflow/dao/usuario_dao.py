from typing import List, Optional

from database.connection import DatabaseConnection
from models.usuario import Usuario


class UsuarioDAO:
    def __init__(self):
        self._db = DatabaseConnection.get_instance()

    def _mapear(self, row) -> Usuario:
        return Usuario(row['id'], row['nome'], row['email'], row['departamento'])

    def criar(self, usuario: Usuario) -> Usuario:
        cursor = self._db.get_cursor()
        cursor.execute(
            "INSERT INTO usuario (nome, email, departamento) VALUES (%s, %s, %s) RETURNING id",
            (usuario.nome, usuario.email, usuario.departamento)
        )
        usuario.id = cursor.fetchone()['id']
        self._db.commit()
        return usuario

    def buscar_por_id(self, id: int) -> Optional[Usuario]:
        cursor = self._db.get_cursor()
        cursor.execute("SELECT * FROM usuario WHERE id = %s", (id,))
        row = cursor.fetchone()
        return self._mapear(row) if row else None

    def buscar_todos(self) -> List[Usuario]:
        cursor = self._db.get_cursor()
        cursor.execute("SELECT * FROM usuario ORDER BY nome")
        return [self._mapear(r) for r in cursor.fetchall()]

    def buscar_por_departamento(self, departamento: str) -> List[Usuario]:
        cursor = self._db.get_cursor()
        cursor.execute(
            "SELECT * FROM usuario WHERE departamento ILIKE %s ORDER BY nome",
            (f'%{departamento}%',)
        )
        return [self._mapear(r) for r in cursor.fetchall()]

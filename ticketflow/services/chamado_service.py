from typing import List, Optional

from dao.chamado_dao import ChamadoDAO
from dao.usuario_dao import UsuarioDAO
from exceptions.chamado_invalido_exception import ChamadoInvalidoException
from models.chamado import Chamado
from models.chamado_financeiro import ChamadoFinanceiro
from models.chamado_infraestrutura import ChamadoInfraestrutura
from models.chamado_rh import ChamadoRH
from models.chamado_ti import ChamadoTI
from models.usuario import Usuario


_TIPO_CLASSE = {
    'TI':             ChamadoTI,
    'RH':             ChamadoRH,
    'FINANCEIRO':     ChamadoFinanceiro,
    'INFRAESTRUTURA': ChamadoInfraestrutura,
}


class ChamadoService:
    def __init__(self):
        self._chamado_dao = ChamadoDAO()
        self._usuario_dao = UsuarioDAO()

    # --- validacao central ---
    def _validar_dados(self, titulo: str, descricao: str, prioridade: str, usuario_id: int) -> Usuario:
        if not titulo or not titulo.strip():
            raise ChamadoInvalidoException("Titulo nao pode ser vazio.")
        if not descricao or not descricao.strip():
            raise ChamadoInvalidoException("Descricao nao pode ser vazia.")
        if prioridade.upper() not in Chamado.PRIORIDADES_VALIDAS:
            raise ChamadoInvalidoException(
                f"Prioridade invalida: '{prioridade}'. Valores aceitos: {Chamado.PRIORIDADES_VALIDAS}"
            )
        usuario = self._usuario_dao.buscar_por_id(usuario_id)
        if not usuario:
            raise ChamadoInvalidoException(f"Usuario com ID {usuario_id} nao encontrado.")
        return usuario

    # --- abertura ---
    def abrir_chamado(
        self,
        tipo: str,
        titulo: str,
        descricao: str,
        prioridade: str,
        usuario_id: int,
        **kwargs
    ) -> Chamado:
        tipo = tipo.upper()
        if tipo not in _TIPO_CLASSE:
            raise ChamadoInvalidoException(
                f"Tipo invalido: '{tipo}'. Valores aceitos: {list(_TIPO_CLASSE.keys())}"
            )
        usuario = self._validar_dados(titulo, descricao, prioridade, usuario_id)
        Classe = _TIPO_CLASSE[tipo]
        chamado = Classe(
            id=None,
            titulo=titulo.strip(),
            descricao=descricao.strip(),
            prioridade=prioridade.upper(),
            status='ABERTO',
            usuario=usuario,
            **kwargs
        )
        return self._chamado_dao.criar(chamado)

    # --- leitura ---
    def buscar_chamado(self, id: int) -> Chamado:
        chamado = self._chamado_dao.buscar_por_id(id)
        if not chamado:
            raise ChamadoInvalidoException(f"Chamado #{id} nao encontrado.")
        return chamado

    def listar_chamados(self) -> List[Chamado]:
        return self._chamado_dao.listar_todos()

    def buscar_por_status(self, status: str) -> List[Chamado]:
        if status.upper() not in Chamado.STATUS_VALIDOS:
            raise ChamadoInvalidoException(
                f"Status invalido: '{status}'. Valores aceitos: {Chamado.STATUS_VALIDOS}"
            )
        return self._chamado_dao.buscar_por_status(status)

    def buscar_por_prioridade(self, prioridade: str) -> List[Chamado]:
        if prioridade.upper() not in Chamado.PRIORIDADES_VALIDAS:
            raise ChamadoInvalidoException(
                f"Prioridade invalida: '{prioridade}'. Valores aceitos: {Chamado.PRIORIDADES_VALIDAS}"
            )
        return self._chamado_dao.buscar_por_prioridade(prioridade)

    def buscar_por_departamento(self, departamento: str) -> List[Chamado]:
        return self._chamado_dao.buscar_por_departamento(departamento)

    def buscar_por_usuario(self, usuario_id: int) -> List[Chamado]:
        return self._chamado_dao.buscar_por_usuario(usuario_id)

    # --- atualizacao ---
    def atualizar_chamado(
        self,
        id: int,
        titulo: str = None,
        descricao: str = None,
        prioridade: str = None,
        **kwargs
    ) -> Chamado:
        chamado = self.buscar_chamado(id)

        if titulo is not None:
            if not titulo.strip():
                raise ChamadoInvalidoException("Titulo nao pode ser vazio.")
            chamado.titulo = titulo.strip()

        if descricao is not None:
            if not descricao.strip():
                raise ChamadoInvalidoException("Descricao nao pode ser vazia.")
            chamado.descricao = descricao.strip()

        if prioridade is not None:
            if prioridade.upper() not in Chamado.PRIORIDADES_VALIDAS:
                raise ChamadoInvalidoException(
                    f"Prioridade invalida: '{prioridade}'. Valores aceitos: {Chamado.PRIORIDADES_VALIDAS}"
                )
            chamado.prioridade = prioridade.upper()

        # Atualiza campos especificos da subclasse via property setters
        for campo, valor in kwargs.items():
            if hasattr(chamado, campo):
                setattr(chamado, campo, valor)

        self._chamado_dao.atualizar(chamado)
        return chamado

    def alterar_status(self, id: int, novo_status: str) -> Chamado:
        chamado = self.buscar_chamado(id)
        chamado.alterar_status(novo_status)  # valida dentro do metodo
        self._chamado_dao.atualizar(chamado)
        return chamado

    # --- encerramento e exclusao ---
    def encerrar_chamado(self, id: int) -> bool:
        self.buscar_chamado(id)  # garante que existe
        return self._chamado_dao.encerrar(id)

    def excluir_chamado(self, id: int) -> bool:
        self.buscar_chamado(id)  # garante que existe
        return self._chamado_dao.excluir(id)

    # --- relatorios ---
    def gerar_relatorio(self) -> dict:
        return {
            'por_departamento': self._chamado_dao.relatorio_por_departamento(),
            'por_status':       self._chamado_dao.relatorio_por_status(),
            'por_prioridade':   self._chamado_dao.relatorio_por_prioridade(),
            'resumo':           self._chamado_dao.relatorio_resumo(),
        }

    def listar_usuarios(self) -> List[Usuario]:
        return self._usuario_dao.buscar_todos()

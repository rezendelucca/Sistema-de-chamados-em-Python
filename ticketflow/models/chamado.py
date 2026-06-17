from abc import ABC, abstractmethod
from datetime import datetime
from models.usuario import Usuario


class Chamado(ABC):
    PRIORIDADES_VALIDAS = ['BAIXA', 'MEDIA', 'ALTA', 'CRITICA']
    STATUS_VALIDOS = ['ABERTO', 'EM_ANDAMENTO', 'ENCERRADO', 'CANCELADO']

    def __init__(
        self,
        id: int,
        titulo: str,
        descricao: str,
        prioridade: str,
        status: str,
        usuario: Usuario,
        data_abertura: datetime = None
    ):
        self._id = id
        self._titulo = titulo
        self._descricao = descricao
        self._prioridade = prioridade.upper()
        self._status = status.upper()
        self._usuario = usuario
        self._data_abertura = data_abertura or datetime.now()

    # --- id ---
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, valor: int):
        self._id = valor

    # --- titulo ---
    @property
    def titulo(self):
        return self._titulo

    @titulo.setter
    def titulo(self, valor: str):
        self._titulo = valor

    # --- descricao ---
    @property
    def descricao(self):
        return self._descricao

    @descricao.setter
    def descricao(self, valor: str):
        self._descricao = valor

    # --- prioridade ---
    @property
    def prioridade(self):
        return self._prioridade

    @prioridade.setter
    def prioridade(self, valor: str):
        self._prioridade = valor.upper()

    # --- status ---
    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, valor: str):
        self._status = valor.upper()

    # --- usuario ---
    @property
    def usuario(self):
        return self._usuario

    # --- data_abertura ---
    @property
    def data_abertura(self):
        return self._data_abertura

    @data_abertura.setter
    def data_abertura(self, valor: datetime):
        self._data_abertura = valor

    def alterar_status(self, novo_status: str):
        novo = novo_status.upper()
        if novo not in self.STATUS_VALIDOS:
            raise ValueError(f"Status invalido: '{novo}'. Use: {self.STATUS_VALIDOS}")
        self._status = novo

    @abstractmethod
    def exibir_detalhes(self):
        pass

    def __str__(self):
        return f"Chamado #{self._id} - {self._titulo} [{self._status}]"

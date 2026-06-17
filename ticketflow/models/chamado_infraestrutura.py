from datetime import datetime
from models.chamado import Chamado
from models.usuario import Usuario


class ChamadoInfraestrutura(Chamado):
    """Chamado de Infraestrutura (instalacoes fisicas, manutencao predial, etc.)."""

    def __init__(
        self,
        id: int,
        titulo: str,
        descricao: str,
        prioridade: str,
        status: str,
        usuario: Usuario,
        local_instalacao: str = None,
        data_abertura: datetime = None
    ):
        super().__init__(id, titulo, descricao, prioridade, status, usuario, data_abertura)
        self._local_instalacao = local_instalacao

    @property
    def local_instalacao(self):
        return self._local_instalacao

    @local_instalacao.setter
    def local_instalacao(self, valor: str):
        self._local_instalacao = valor

    def exibir_detalhes(self):
        linha = "=" * 52
        print(linha)
        print(f"  CHAMADO INFRAESTRUTURA  #{self._id}")
        print(linha)
        print(f"  Titulo            : {self._titulo}")
        print(f"  Descricao         : {self._descricao}")
        print(f"  Local Instalacao  : {self._local_instalacao or 'Nao informado'}")
        print(f"  Prioridade        : {self._prioridade}")
        print(f"  Status            : {self._status}")
        print(f"  Solicitante       : {self._usuario.nome} ({self._usuario.departamento})")
        print(f"  Abertura          : {self._data_abertura.strftime('%d/%m/%Y %H:%M')}")
        print(linha)

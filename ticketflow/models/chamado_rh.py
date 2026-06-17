from datetime import datetime
from models.chamado import Chamado
from models.usuario import Usuario


class ChamadoRH(Chamado):
    """Chamado de Recursos Humanos (contratacoes, beneficios, folha, etc.)."""

    def __init__(
        self,
        id: int,
        titulo: str,
        descricao: str,
        prioridade: str,
        status: str,
        usuario: Usuario,
        cargo_afetado: str = None,
        data_abertura: datetime = None
    ):
        super().__init__(id, titulo, descricao, prioridade, status, usuario, data_abertura)
        self._cargo_afetado = cargo_afetado

    @property
    def cargo_afetado(self):
        return self._cargo_afetado

    @cargo_afetado.setter
    def cargo_afetado(self, valor: str):
        self._cargo_afetado = valor

    def exibir_detalhes(self):
        linha = "=" * 52
        print(linha)
        print(f"  CHAMADO RH  #{self._id}")
        print(linha)
        print(f"  Titulo        : {self._titulo}")
        print(f"  Descricao     : {self._descricao}")
        print(f"  Cargo Afetado : {self._cargo_afetado or 'Nao informado'}")
        print(f"  Prioridade    : {self._prioridade}")
        print(f"  Status        : {self._status}")
        print(f"  Solicitante   : {self._usuario.nome} ({self._usuario.departamento})")
        print(f"  Abertura      : {self._data_abertura.strftime('%d/%m/%Y %H:%M')}")
        print(linha)

from datetime import datetime
from models.chamado import Chamado
from models.usuario import Usuario


class ChamadoTI(Chamado):
    """Chamado de Tecnologia da Informacao (Hardware, Software, Rede, Seguranca)."""

    def __init__(
        self,
        id: int,
        titulo: str,
        descricao: str,
        prioridade: str,
        status: str,
        usuario: Usuario,
        categoria_ti: str = None,
        data_abertura: datetime = None
    ):
        super().__init__(id, titulo, descricao, prioridade, status, usuario, data_abertura)
        self._categoria_ti = categoria_ti

    @property
    def categoria_ti(self):
        return self._categoria_ti

    @categoria_ti.setter
    def categoria_ti(self, valor: str):
        self._categoria_ti = valor

    def exibir_detalhes(self):
        linha = "=" * 52
        print(linha)
        print(f"  CHAMADO TI  #{self._id}")
        print(linha)
        print(f"  Titulo       : {self._titulo}")
        print(f"  Descricao    : {self._descricao}")
        print(f"  Categoria TI : {self._categoria_ti or 'Nao informada'}")
        print(f"  Prioridade   : {self._prioridade}")
        print(f"  Status       : {self._status}")
        print(f"  Solicitante  : {self._usuario.nome} ({self._usuario.departamento})")
        print(f"  Abertura     : {self._data_abertura.strftime('%d/%m/%Y %H:%M')}")
        print(linha)

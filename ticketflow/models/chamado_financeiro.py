from datetime import datetime
from models.chamado import Chamado
from models.usuario import Usuario


class ChamadoFinanceiro(Chamado):
    """Chamado do setor Financeiro (orcamentos, reembolsos, pagamentos, etc.)."""

    def __init__(
        self,
        id: int,
        titulo: str,
        descricao: str,
        prioridade: str,
        status: str,
        usuario: Usuario,
        centro_custo: str = None,
        data_abertura: datetime = None
    ):
        super().__init__(id, titulo, descricao, prioridade, status, usuario, data_abertura)
        self._centro_custo = centro_custo

    @property
    def centro_custo(self):
        return self._centro_custo

    @centro_custo.setter
    def centro_custo(self, valor: str):
        self._centro_custo = valor

    def exibir_detalhes(self):
        linha = "=" * 52
        print(linha)
        print(f"  CHAMADO FINANCEIRO  #{self._id}")
        print(linha)
        print(f"  Titulo          : {self._titulo}")
        print(f"  Descricao       : {self._descricao}")
        print(f"  Centro de Custo : {self._centro_custo or 'Nao informado'}")
        print(f"  Prioridade      : {self._prioridade}")
        print(f"  Status          : {self._status}")
        print(f"  Solicitante     : {self._usuario.nome} ({self._usuario.departamento})")
        print(f"  Abertura        : {self._data_abertura.strftime('%d/%m/%Y %H:%M')}")
        print(linha)

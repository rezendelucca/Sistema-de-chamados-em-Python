class ChamadoInvalidoException(Exception):
    def __init__(self, mensagem: str):
        super().__init__(mensagem)
        self.mensagem = mensagem

    def __str__(self):
        return f"[ChamadoInvalido] {self.mensagem}"

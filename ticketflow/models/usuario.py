class Usuario:
    def __init__(self, id: int, nome: str, email: str, departamento: str):
        self._id = id
        self._nome = nome
        self._email = email
        self._departamento = departamento

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, valor: int):
        self._id = valor

    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, valor: str):
        if not valor or not valor.strip():
            raise ValueError("Nome nao pode ser vazio.")
        self._nome = valor.strip()

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, valor: str):
        self._email = valor

    @property
    def departamento(self):
        return self._departamento

    @departamento.setter
    def departamento(self, valor: str):
        self._departamento = valor

    def __str__(self):
        return f"Usuario(id={self._id}, nome={self._nome}, departamento={self._departamento})"

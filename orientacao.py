"""Classe Orientacao: guarda os dados de uma orientação da base e a exibe na tela."""

AVISO = "este assistente NÃO é um canal oficial."

CAMPOS_OBRIGATORIOS = (
    "id", "categoria", "titulo", "palavras_chave", "resposta",
    "documentos", "onde", "fonte", "verificado_em",
)


class Orientacao:
    """Uma informação da base de conhecimento (um registro do JSON)."""

    def __init__(self, id, categoria, titulo, palavras_chave, resposta,
                 documentos, onde, fonte, verificado_em):
        self.id = id
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave
        self.resposta = resposta
        self.documentos = documentos
        self.onde = onde
        self.fonte = fonte
        self.verificado_em = verificado_em

    @staticmethod
    def registro_valido(registro):
        """Confere se um dicionário do JSON tem todos os campos com o tipo certo."""
        if not isinstance(registro, dict):
            return False
        for campo in CAMPOS_OBRIGATORIOS:
            if campo not in registro:
                return False
        if not isinstance(registro["id"], int) or isinstance(registro["id"], bool):
            return False
        for campo in ("categoria", "titulo", "resposta", "onde", "fonte", "verificado_em"):
            if not isinstance(registro[campo], str) or not registro[campo].strip():
                return False
        for campo in ("palavras_chave", "documentos"):
            lista = registro[campo]
            if not isinstance(lista, list) or not all(isinstance(x, str) for x in lista):
                return False
        return len(registro["palavras_chave"]) > 0

    @classmethod
    def de_dicionario(cls, registro):
        """Cria um objeto Orientacao a partir de um dicionário do JSON."""
        return cls(
            registro["id"], registro["categoria"], registro["titulo"],
            registro["palavras_chave"], registro["resposta"],
            registro["documentos"], registro["onde"],
            registro["fonte"], registro["verificado_em"],
        )

    def exibir(self):
        """Mostra a orientação na tela, com fonte, data de verificação e aviso."""
        print(f">> {self.titulo}  [{self.categoria}]")
        print(self.resposta)
        print("Documentos necessários:")
        for documento in self.documentos:
            print(f"  - {documento}")
        print(f"Onde: {self.onde}")
        print(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        print(f"Aviso: {AVISO}")

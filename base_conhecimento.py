"""Classe BaseConhecimento: lê o JSON, lista categorias e busca a melhor orientação."""

import json

from orientacao import Orientacao

ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "ä": "a",
           "é": "e", "è": "e", "ê": "e", "ë": "e",
           "í": "i", "ì": "i", "ï": "i",
           "ó": "o", "ò": "o", "õ": "o", "ô": "o", "ö": "o",
           "ú": "u", "ù": "u", "ü": "u", "ç": "c", "ñ": "n"}

SINAIS = "?!.,;:()[]{}\"'-/\\_*#%&+=<>|"

# Palavras comuns que não dizem nada sobre o assunto: não ganham ponto no título.
PALAVRAS_VAZIAS = {
    "como", "para", "pode", "posso", "quero", "preciso", "onde", "quando",
    "qual", "quais", "tenho", "fazer", "minha", "meu", "pelo", "pela",
    "sobre", "mais", "isso", "esta", "esse", "essa", "para", "com",
}

PONTOS_PALAVRA_CHAVE = 3
PONTOS_TITULO = 1
MINIMO_MEDIA = 3
MINIMO_ALTA = 6


def normalizar(texto):
    """Minúsculas, sem acentos e sem pontuação; devolve com espaço nas pontas."""
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in SINAIS:
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


class BaseConhecimento:
    """O conjunto de todas as orientações."""

    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []
        self.erro = ""

    def carregar(self):
        """Lê o JSON e cria os objetos Orientacao. Nunca levanta erro: devolve True/False."""
        self.orientacoes = []
        self.erro = ""
        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            self.erro = f"Arquivo da base não encontrado: {self.caminho}"
            return False
        except json.JSONDecodeError:
            self.erro = f"Arquivo da base está corrompido: {self.caminho}"
            return False
        except (OSError, UnicodeDecodeError):
            self.erro = f"Não foi possível ler o arquivo da base: {self.caminho}"
            return False

        if not isinstance(dados, list):
            self.erro = "A base deve ser uma lista de orientações."
            return False

        ignorados = 0
        for registro in dados:
            if Orientacao.registro_valido(registro):
                self.orientacoes.append(Orientacao.de_dicionario(registro))
            else:
                ignorados += 1

        if not self.orientacoes:
            self.erro = "Nenhuma orientação válida na base."
            return False
        if ignorados:
            self.erro = f"{ignorados} registro(s) inválido(s) foram ignorados."
        return True

    def categorias(self):
        """Lista as categorias, sem repetir, na ordem em que aparecem."""
        lista = []
        for orientacao in self.orientacoes:
            if orientacao.categoria not in lista:
                lista.append(orientacao.categoria)
        return lista

    def por_categoria(self, categoria):
        """Devolve as orientações de uma categoria."""
        return [o for o in self.orientacoes if o.categoria == categoria]

    def pontuar(self, pergunta, orientacao):
        """Dá pontos a uma orientação para uma pergunta (regras da seção 6.2)."""
        pergunta_norm = normalizar(pergunta)
        titulo_norm = normalizar(orientacao.titulo)
        pontos = 0

        # +3 por palavra-chave da orientação que aparece na pergunta
        for palavra_chave in orientacao.palavras_chave:
            if normalizar(palavra_chave) in pergunta_norm:
                pontos += PONTOS_PALAVRA_CHAVE

        # +1 por palavra da pergunta (4 letras ou mais) que aparece no título
        vistas = set()
        for palavra in pergunta_norm.split():
            if len(palavra) < 4 or palavra in PALAVRAS_VAZIAS or palavra in vistas:
                continue
            vistas.add(palavra)
            if f" {palavra} " in titulo_norm:
                pontos += PONTOS_TITULO
        return pontos

    def buscar(self, pergunta):
        """Devolve lista de tuplas (pontos, orientacao), da maior para a menor pontuação."""
        resultados = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(pergunta, orientacao)
            if pontos > 0:
                resultados.append((pontos, orientacao))
        resultados.sort(key=lambda tupla: (-tupla[0], tupla[1].id))
        return resultados

    @staticmethod
    def confianca(pontos):
        """ALTA (6+), MEDIA (3 a 5) ou None (menos de 3 pontos)."""
        if pontos >= MINIMO_ALTA:
            return "ALTA"
        if pontos >= MINIMO_MEDIA:
            return "MÉDIA"
        return None

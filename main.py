"""Citizen Assist AI: assistente digital de orientação para pessoas idosas (terminal)."""

import os
import sys

from assistente import Assistente, ler
from base_conhecimento import BaseConhecimento

# Garante que os caminhos data/... funcionem de qualquer pasta onde o programa seja executado.
PASTA = os.path.dirname(os.path.abspath(__file__))
CAMINHO_BASE = os.path.join(PASTA, "data", "base_conhecimento.json")
CAMINHO_HISTORICO = os.path.join(PASTA, "data", "historico.json")
CAMINHO_CSV = os.path.join(PASTA, "data", "atendimentos.csv")


def configurar_saida():
    """Evita erro de acentuação em terminais que não usam UTF-8."""
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


def mostrar_menu(nome) -> None:
    print()
    print(f"===== {nome} =====")
    print("1. Fazer uma pergunta")
    print("2. Navegar por categorias")
    print("3. Ver indicadores")
    print("4. Exportar atendimentos para CSV")
    print("0. Sair")
    return

def main():
    configurar_saida()

    base = BaseConhecimento(CAMINHO_BASE)
    carregou = base.carregar()
    if not carregou:
        print(f"Aviso: {base.erro}")
    elif base.erro:
        print(f"Aviso: {base.erro}")

    assistente = Assistente("Citizen Assist AI", base, CAMINHO_HISTORICO, CAMINHO_CSV)

    print("Olá! Eu sou o Citizen Assist AI.")
    print("Respondo dúvidas de pessoas idosas com base em informações de fontes oficiais.")
    print("Não peço nem guardo dados pessoais. Este assistente NÃO é um canal oficial.")

    while True:
        mostrar_menu(assistente.nome)
        opcao = ler("Escolha uma opção: ").strip()
        match opcao:
            case "1":
                assistente.perguntar()
            case "2":
                assistente.navegar()
            case "3":
                assistente.exibir_indicadores()
            case "4":
                assistente.exportar_csv()
            case "0":
                break
            case _:
                print('Opção inválida. Escolha um número de 0 a 4.')


    assistente.pedir_nota()
    assistente.exportar_csv()
    print("Até logo! Lembre-se: confirme sempre nos canais oficiais.")


if __name__ == "__main__":
    main()
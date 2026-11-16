"""Classe Assistente: faz o atendimento, guarda o histórico e calcula os indicadores."""

import csv
import json
import os
import time
from datetime import datetime

from base_conhecimento import BaseConhecimento

CAMINHO_HISTORICO = "data/historico.json"
CAMINHO_CSV = "data/atendimentos.csv"

CAMPOS_CSV = ["data", "sessao", "origem", "pergunta", "id_orientacao",
              "encontrou", "ajudou", "tentativas", "tempo_s", "nota_facilidade"]

MENSAGEM_DADO_PESSOAL = "Atenção: não digite CPF, telefone ou e-mail. Reescreva."


def ler(mensagem):
    """input() que nunca derruba o programa (Ctrl+C, Ctrl+D ou fim da entrada viram '0')."""
    try:
        return input(mensagem)
    except (EOFError, KeyboardInterrupt):
        print()
        return "0"


def tem_dado_pessoal(texto):
    """True se o texto tem 8 ou mais dígitos ou um @ (CPF, telefone, e-mail)."""
    digitos = sum(1 for letra in texto if letra.isdigit())
    return digitos >= 8 or "@" in texto


def perguntar_sim_nao(mensagem):
    """Repete até a pessoa responder s ou n. Devolve True para s."""
    while True:
        resposta = ler(mensagem).strip().lower()
        if resposta in ("s", "sim"):
            return True
        if resposta in ("n", "nao", "não"):
            return False
        print("Resposta inválida. Digite s para sim ou n para não.")


class Assistente:
    """Quem conversa com o cidadão."""

    def __init__(self, nome, base, caminho_historico=CAMINHO_HISTORICO,
                 caminho_csv=CAMINHO_CSV):
        self.nome = nome
        self.base = base
        self.caminho_historico = caminho_historico
        self.caminho_csv = caminho_csv
        self.sessao = datetime.now().strftime("%Y%m%d%H%M%S")
        self.historico = self._carregar_historico()
        self.registrados_na_sessao = 0

    # ------------------------------------------------------------------ histórico
    def _carregar_historico(self):
        """Lê historico.json. Se faltar ou estiver corrompido, começa vazio sem travar."""
        try:
            with open(self.caminho_historico, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            return []
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            print("Aviso: o histórico estava ilegível e foi guardado como cópia (.bak).")
            try:
                os.replace(self.caminho_historico, self.caminho_historico + ".bak")
            except OSError:
                pass
            return []
        if not isinstance(dados, list):
            return []
        return [item for item in dados if isinstance(item, dict)]

    def _salvar_historico(self):
        try:
            pasta = os.path.dirname(self.caminho_historico)
            if pasta:
                os.makedirs(pasta, exist_ok=True)
            with open(self.caminho_historico, "w", encoding="utf-8") as arquivo:
                json.dump(self.historico, arquivo, ensure_ascii=False, indent=2)
        except OSError:
            print("Aviso: não foi possível salvar o histórico.")

    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou,
                  tentativas, tempo_s):
        """Guarda um atendimento em historico.json."""
        atendimento = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sessao": self.sessao,
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": id_orientacao,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_s": tempo_s,
        }
        self.historico.append(atendimento)
        self.registrados_na_sessao += 1
        self._salvar_historico()

    # ------------------------------------------------------------------ atendimento
    def _mostrar_resultado(self, resultados):
        """Mostra a melhor orientação e até duas alternativas. Devolve a melhor."""
        pontos, melhor = resultados[0]
        print()
        print(f"Confiança da resposta: {BaseConhecimento.confianca(pontos)} ({pontos} pontos)")
        print()
        melhor.exibir()
        alternativas = [(p, o) for p, o in resultados[1:3]
                        if BaseConhecimento.confianca(p) is not None]
        if alternativas:
            print()
            print("Veja também:")
            for p, o in alternativas:
                print(f"  - {o.titulo} [{o.categoria}] ({p} pontos)")
        print()
        return melhor

    def _sugerir_outras_formas(self):
        print()
        print("Não encontrei uma orientação para essa dúvida.")
        print("Tente outras palavras (ex.: cartão SUS, ônibus gratuito, golpe, INSS)")
        print("ou use a opção de navegar por categorias:")
        for categoria in self.base.categorias():
            print(f"  - {categoria}")
        print()

    def perguntar(self):
        """Atendimento por texto livre. Digite 0 para voltar."""
        if not self.base.orientacoes:
            print("A base de conhecimento não está disponível. Tente a navegação mais tarde.")
            return

        inicio = time.time()
        tentativas = 0
        ultima_pergunta = ""
        encontrou = False
        ajudou = False
        id_orientacao = None

        while True:
            texto = ler("Digite sua dúvida (0 para voltar): ").strip()
            if texto == "0":
                break
            if not texto:
                print("Você não digitou nada. Escreva sua dúvida ou 0 para voltar.")
                continue
            if tem_dado_pessoal(texto):
                # recusada: não conta como tentativa e não é registrada
                print(MENSAGEM_DADO_PESSOAL)
                continue

            tentativas += 1
            ultima_pergunta = texto
            resultados = self.base.buscar(texto)

            if not resultados or BaseConhecimento.confianca(resultados[0][0]) is None:
                encontrou = False
                ajudou = False
                id_orientacao = None
                self._sugerir_outras_formas()
                continue

            encontrou = True
            melhor = self._mostrar_resultado(resultados)
            id_orientacao = melhor.id
            ajudou = perguntar_sim_nao("Essa orientação respondeu sua dúvida? (s/n): ")
            print()
            if ajudou:
                break

        if tentativas > 0:
            tempo = round(time.time() - inicio, 1)
            self.registrar("pergunta", ultima_pergunta, id_orientacao,
                           encontrou, ajudou, tentativas, tempo)

    def _escolher_numero(self, mensagem, maximo):
        """Pede um número de 0 a maximo. Devolve None se a entrada for inválida."""
        texto = ler(mensagem).strip()
        if not texto.isdigit():
            print("Opção inválida. Digite apenas o número da opção.")
            return None
        numero = int(texto)
        if numero < 0 or numero > maximo:
            print(f"Opção fora da faixa. Escolha de 0 a {maximo}.")
            return None
        return numero

    def navegar(self):
        """Navegação por categorias. 0 volta em todas as telas."""
        if not self.base.orientacoes:
            print("A base de conhecimento não está disponível.")
            return

        categorias = self.base.categorias()
        while True:
            print()
            print("=== Categorias ===")
            for i, categoria in enumerate(categorias, start=1):
                print(f"{i}. {categoria}")
            print("0. Voltar")
            escolha = self._escolher_numero("Escolha uma categoria: ", len(categorias))
            if escolha is None:
                continue
            if escolha == 0:
                return
            self._navegar_categoria(categorias[escolha - 1])

    def _navegar_categoria(self, categoria):
        orientacoes = self.base.por_categoria(categoria)
        while True:
            print()
            print(f"=== {categoria} ===")
            for i, orientacao in enumerate(orientacoes, start=1):
                print(f"{i}. {orientacao.titulo}")
            print("0. Voltar")
            inicio = time.time()
            escolha = self._escolher_numero("Escolha uma orientação: ", len(orientacoes))
            if escolha is None:
                continue
            if escolha == 0:
                return
            orientacao = orientacoes[escolha - 1]
            print()
            orientacao.exibir()
            print()
            ajudou = perguntar_sim_nao("Essa orientação respondeu sua dúvida? (s/n): ")
            tempo = round(time.time() - inicio, 1)
            self.registrar("categoria", f"[categoria] {categoria}", orientacao.id,
                           True, ajudou, 1, tempo)

    # ------------------------------------------------------------------ nota e indicadores
    def pedir_nota(self):
        """Ao sair, pede a nota de facilidade (1 a 5) e guarda nos atendimentos da sessão."""
        if self.registrados_na_sessao == 0:
            return
        while True:
            texto = ler("De 1 a 5, quão fácil foi usar o assistente? ").strip()
            if texto in ("1", "2", "3", "4", "5"):
                nota = int(texto)
                break
            print("Nota inválida. Digite um número de 1 a 5.")
        for atendimento in self.historico:
            if atendimento.get("sessao") == self.sessao:
                atendimento["nota_facilidade"] = nota
        self._salvar_historico()

    def indicadores(self):
        """Calcula os indicadores a partir do histórico. Devolve um dicionário."""
        total = len(self.historico)
        if total == 0:
            return {"total": 0}

        encontrados = [a for a in self.historico if a.get("encontrou")]
        ajudados = [a for a in self.historico if a.get("ajudou")]

        tempos = [a["tempo_s"] for a in encontrados
                  if isinstance(a.get("tempo_s"), (int, float))]
        tentativas = [a["tentativas"] for a in self.historico
                      if isinstance(a.get("tentativas"), (int, float))]

        # uma nota por sessão (por pessoa), para não contar a mesma nota várias vezes
        notas_por_sessao = {}
        for a in self.historico:
            nota = a.get("nota_facilidade")
            if isinstance(nota, int) and 1 <= nota <= 5:
                notas_por_sessao[a.get("sessao")] = nota

        sem_solucao = []
        for a in self.historico:
            if a.get("origem") == "pergunta" and (not a.get("encontrou") or not a.get("ajudou")):
                if a.get("pergunta") and a["pergunta"] not in sem_solucao:
                    sem_solucao.append(a["pergunta"])

        return {
            "total": total,
            "encontrada_pct": round(100 * len(encontrados) / total, 1),
            "acerto_pct": round(100 * len(ajudados) / total, 1),
            "tempo_medio": round(sum(tempos) / len(tempos), 1) if tempos else None,
            "tentativas_media": round(sum(tentativas) / len(tentativas), 1) if tentativas else None,
            "facilidade": (round(sum(notas_por_sessao.values()) / len(notas_por_sessao), 1)
                           if notas_por_sessao else None),
            "sem_solucao": sem_solucao,
        }

    def exibir_indicadores(self):
        dados = self.indicadores()
        print()
        print("=== Indicadores ===")
        if dados["total"] == 0:
            print("Ainda não há atendimentos registrados.")
            return

        def formatar(valor, sufixo=""):
            return "sem dados" if valor is None else f"{valor}{sufixo}"

        print(f"Atendimentos registrados:  {dados['total']}")
        print(f"Resposta encontrada (%):   {dados['encontrada_pct']}")
        print(f"Taxa de acerto: ajudou (%): {dados['acerto_pct']}")
        print(f"Tempo médio para encontrar: {formatar(dados['tempo_medio'], ' s')}")
        print(f"Tentativas por atendimento: {formatar(dados['tentativas_media'])}")
        print(f"Facilidade de uso (1 a 5):  {formatar(dados['facilidade'])}")
        print("Dúvidas sem solução:")
        if dados["sem_solucao"]:
            for duvida in dados["sem_solucao"]:
                print(f"  - {duvida}")
        else:
            print("  (nenhuma)")

    # ------------------------------------------------------------------ CSV
    def exportar_csv(self):
        """Exporta os atendimentos para data/atendimentos.csv com csv.DictWriter."""
        try:
            pasta = os.path.dirname(self.caminho_csv)
            if pasta:
                os.makedirs(pasta, exist_ok=True)
            with open(self.caminho_csv, "w", newline="", encoding="utf-8") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_CSV, extrasaction="ignore")
                escritor.writeheader()
                for atendimento in self.historico:
                    linha = dict(atendimento)
                    for campo in ("encontrou", "ajudou"):
                        if campo in linha:
                            linha[campo] = "sim" if linha[campo] else "nao"
                    escritor.writerow(linha)
        except OSError:
            print("Não foi possível salvar o arquivo CSV.")
            return False
        print(f"{len(self.historico)} atendimento(s) exportado(s) para {self.caminho_csv}")
        return True

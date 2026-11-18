# Citizen Assist AI

Assistente de terminal, feito em Python, que orienta **pessoas idosas** sobre saúde, benefícios, direitos, transporte, golpes e serviços digitais. Ele só responde com o que está na base de conhecimento (`data/base_conhecimento.json`), sempre mostra a **fonte**, a **data de verificação** e o aviso de que **não é um canal oficial**, e **nunca coleta dados pessoais**.

> Global Solution 2026.2 — Pensamento Computacional e Automação com Python (FIAP) — desafio CitizenTech.

## Integrantes

| Nome | RM |
|------|----|
| [Felipe Alves Canazza] | [572470] |
| [Pedro Andreaza] | [571107] |
| [Eduardo Reis] | [569727] |

## Público e problema escolhidos

- **Público:** pessoas idosas (60 anos ou mais) e familiares que ajudam com os trâmites.
- **Problema:** a informação sobre Cartão SUS, vacinas, remédios gratuitos, BPC, transporte gratuito e golpes existe, mas está espalhada, em linguagem técnica e misturada com páginas falsas que parecem oficiais. O assistente reúne orientações verificadas em linguagem simples, diz onde ir, o que levar e de onde veio a informação.

## ODS relacionados

- **ODS 3 – Saúde e Bem-Estar** (acesso ao SUS, vacinação, medicamentos).
- **ODS 10 – Redução das Desigualdades** (direitos e benefícios para quem tem menos acesso à informação).
- **ODS 16 – Paz, Justiça e Instituições Eficazes** (acesso à informação, denúncia de violência e proteção contra fraudes).

## Como executar

Requisito: Python 3.8 ou mais novo. Não usa bibliotecas externas.

```bash
python main.py
```

Menu principal:

1. Fazer uma pergunta (texto livre, com busca por pontuação)
2. Navegar por categorias (0 volta em todas as telas)
3. Ver indicadores
4. Exportar atendimentos para CSV
0. Sair (pede a nota de facilidade de 1 a 5)

## Estrutura

```
citizen-assist-ai/
├── README.md
├── main.py                 # menu principal
├── orientacao.py           # classe Orientacao
├── base_conhecimento.py    # classe BaseConhecimento (+ normalizar)
├── assistente.py           # classe Assistente
└── data/
    ├── base_conhecimento.json
    ├── historico.json
    └── atendimentos.csv
```

Composição: `Assistente` → `base: BaseConhecimento` → `orientacoes: [Orientacao, ...]`.

| Classe | Atributos | Métodos |
|--------|-----------|---------|
| `Orientacao` | id, categoria, titulo, palavras_chave, resposta, documentos, onde, fonte, verificado_em | `exibir()` |
| `BaseConhecimento` | caminho, orientacoes | `carregar()`, `categorias()`, `por_categoria()`, `pontuar()`, `buscar()` |
| `Assistente` | nome, base, historico | `perguntar()`, `navegar()`, `registrar()`, `indicadores()`, `exportar_csv()` |

## Regra de pontuação

A pergunta, as palavras-chave e o título são normalizados por `normalizar()` (minúsculas, sem acentos e sem pontuação). Cada orientação recebe pontos:

| Regra | Pontos |
|-------|--------|
| Palavra-chave da orientação que aparece na pergunta | +3 |
| Palavra da pergunta (4 letras ou mais) que aparece no título | +1 |

| Melhor pontuação | Resultado |
|------------------|-----------|
| 6 pontos ou mais | Confiança **ALTA** |
| 3 a 5 pontos | Confiança **MÉDIA** |
| Menos de 3 pontos | "Não encontrei": sugere outras palavras e as categorias |

`buscar()` devolve uma lista de tuplas `(pontos, orientacao)`, da maior para a menor pontuação (empate: menor `id` primeiro). O assistente mostra a melhor orientação e até duas alternativas com pelo menos 3 pontos.

Exemplo: "Como faço o cartão do SUS?" → `cartao do sus` (+3), `sus` (+3), `cartao` no título (+1) = **7 pontos, confiança ALTA**.

Ajustes feitos pela equipe (previstos no enunciado):

- Cada palavra da pergunta vale no máximo +1 no título, mesmo que se repita.
- Palavras muito comuns (como, para, quero, preciso, fazer...) não ganham ponto no título, para não dar pontos por palavras que não dizem o assunto.
- A palavra-chave só conta quando aparece como palavra inteira (por isso `normalizar()` coloca um espaço nas pontas do texto).

## Regras de atendimento

- **Entradas inválidas** (opção fora da faixa, letras, resposta vazia, s/n inválido) nunca encerram o programa.
- **Dados pessoais:** o assistente nunca pede nome, CPF, telefone ou e-mail. Pergunta com 8 ou mais dígitos ou com `@` é recusada e **não é registrada**.
- **Transparência:** toda resposta mostra fonte, data de verificação e o aviso "este assistente NÃO é um canal oficial".
- **Arquivos:** base ausente ou corrompida não trava o programa (aviso na tela). Histórico ilegível é guardado como `historico.json.bak` e um novo começa vazio.

## Histórico, indicadores e CSV

Cada atendimento é salvo em `data/historico.json` com: data, sessão, origem (`pergunta` ou `categoria`), pergunta, id da orientação, se encontrou, se ajudou, tentativas, tempo em segundos e (ao sair) a nota de facilidade. Os atendimentos são exportados para `data/atendimentos.csv` com `csv.DictWriter` (a opção 4 e também ao sair).

Como o atendimento é contado:

- Um atendimento por texto livre começa na primeira pergunta e termina quando a pessoa diz que a orientação ajudou (s) ou digita 0. Se a pessoa reescrever a pergunta, isso soma em **tentativas**. O resultado registrado é o da última tentativa.
- Na navegação por categorias, cada orientação aberta é um atendimento (1 tentativa).
- A nota de facilidade (1 a 5) é pedida ao sair, quando houve pelo menos um atendimento na sessão. No indicador, cada sessão (pessoa) conta uma vez.

Indicadores exibidos: resposta encontrada (%), taxa de acerto: ajudou (%), tempo médio para encontrar, tentativas por atendimento, facilidade de uso (1 a 5) e lista de dúvidas sem solução.

## Integrações com outras disciplinas

[PREENCHER: se a equipe conectar o projeto a outra disciplina da GS, explique aqui. Se não houver, escreva "Nenhuma integração nesta entrega".]

## Fontes consultadas

Todas as orientações trazem a fonte oficial e a data de verificação no próprio JSON. Principais fontes:

- Ministério da Saúde / gov.br/saude: Cartão SUS, Meu SUS Digital, vacinação (gov.br/vacinacao), Farmácia Popular
- INSS / gov.br/inss: Meu INSS, Central 135, alertas de golpe e prova de vida
- Estatuto da Pessoa Idosa (Lei 10.741/2003) e Lei 10.048/2000 (atendimento prioritário), no portal do Planalto
- ANTT: cartilha do idoso (transporte interestadual)
- Ministério dos Direitos Humanos: Disque 100 (gov.br/mdh/pt-br/ondh)
- Consumidor.gov.br
- gov.br/governodigital: níveis da conta gov.br

> Antes de entregar, a equipe deve abrir cada link, conferir a informação e atualizar o campo `verificado_em` com a data real da conferência.

## Resultado do teste com usuários

> A equipe deve testar com pelo menos **3 pessoas de fora da equipe**, somando **10 atendimentos ou mais**, e preencher abaixo. Não registrar nomes nem dados dessas pessoas.

- Pessoas testadas: [3]
- Atendimentos: [15]
- Resposta encontrada (%): [80.0]
- Taxa de acerto: ajudou (%): [67.0]
- Tempo médio para encontrar: [17.4] s
- Tentativas por atendimento: [1.5]
- Facilidade de uso (1 a 5): [1,5]
- Dúvidas sem solução: [2 duvidas]
- **Melhoria feita a partir do teste:** [algumas perguntas dos usuários não foram encontradas por usarem palavras diferentes das cadastradas. Para resolver, incluímos novas palavras-chave nas orientações do arquivo base_conhecimento.json, e as mesmas perguntas passaram a ser encontradas.]

## Limitações

- A busca é por regras: só entende palavras-chave que estão no JSON; erros de digitação e sinônimos não cadastrados não são encontrados.
- A base tem 13 orientações e reflete as regras federais; regras de cidade e estado (por exemplo, gratuidade de ônibus entre 60 e 64 anos) variam e o assistente apenas avisa para confirmar localmente.
- Valores, prazos e regras mudam; por isso cada resposta mostra a data de verificação.
- O assistente não é canal oficial e não substitui o atendimento do órgão responsável.

## Vídeo técnico

Link (YouTube, não listado): [https://youtu.be/MC37azVLwIM?is=YvhC8ltAdkET-JTk]

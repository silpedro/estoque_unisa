"""Backend: modelo, estruturas de dados, regras de negocio e persistencia."""

import csv
import math
from dataclasses import dataclass
from pathlib import Path


TAMANHO_MAX_DESCRICAO = 50
TAMANHO_MAX_NOME_CATEGORIA = 40
MAXIMO_TAMANHOS_LOTE = 50
NUMERO_MAXIMO = 999
TOTAL_SIGLAS = 26 * 26

CAMPOS_CSV = ["codigo", "descricao", "quantidade", "estoque_minimo", "preco"]
CAMPOS_CATEGORIAS = ["sigla", "nome"]
CAMPOS_SEQUENCIAS = ["sigla", "ultimo_numero"]
CATEGORIAS_PADRAO = [
    ("EP", "Equipamento de Protecao Individual"),
    ("UV", "Uniforme e Vestimenta"),
]
ERRO_CODIGO = "Código inválido. Use 2 letras e 3 dígitos (ex.: UV001)."
ERRO_SIGLA = "Sigla inválida. Use 2 letras (ex.: UV)."


@dataclass
class Produto:
    codigo: int
    descricao: str
    quantidade: int
    estoque_minimo: int
    preco: float


def _so_letras(texto):
    return all("A" <= caractere <= "Z" for caractere in texto)


def _so_digitos(texto):
    return all("0" <= caractere <= "9" for caractere in texto)


def interpretar_sigla(texto):
    """Normaliza a sigla (ex.: ' uv ' -> 'UV') ou lança ValueError."""
    sigla = texto.strip().upper()
    if len(sigla) != 2 or not _so_letras(sigla):
        raise ValueError(ERRO_SIGLA)
    return sigla


def indice_sigla(sigla):
    return (ord(sigla[0]) - ord("A")) * 26 + ord(sigla[1]) - ord("A")


def sigla_do_codigo(codigo):
    indice = codigo // 1000
    return chr(ord("A") + indice // 26) + chr(ord("A") + indice % 26)


def montar_codigo(sigla, numero):
    return indice_sigla(sigla) * 1000 + numero


def codigo_valido(codigo):
    return 0 < codigo < TOTAL_SIGLAS * 1000 and codigo % 1000 != 0


def formatar_codigo(codigo):
    return f"{sigla_do_codigo(codigo)}{codigo % 1000:03d}"


def interpretar_codigo(texto):
    """Converte, por exemplo, 'uv001' em código interno."""
    texto = texto.strip().upper()
    if len(texto) != 5 or not _so_letras(texto[:2]) or not _so_digitos(texto[2:]):
        raise ValueError(ERRO_CODIGO)
    numero = int(texto[2:])
    if numero == 0:
        raise ValueError(ERRO_CODIGO)
    return montar_codigo(texto[:2], numero)


def validar_produto(produto):
    """Lança ValueError se algum campo do produto for inválido."""
    if not codigo_valido(produto.codigo):
        raise ValueError(ERRO_CODIGO)
    if not produto.descricao.strip():
        raise ValueError("A descrição é obrigatória.")
    if len(produto.descricao) > TAMANHO_MAX_DESCRICAO:
        raise ValueError(f"A descrição deve ter até {TAMANHO_MAX_DESCRICAO} caracteres.")
    if ";" in produto.descricao or '"' in produto.descricao:
        raise ValueError("A descrição não pode conter ';' nem aspas.")
    if produto.quantidade < 0 or produto.estoque_minimo < 0:
        raise ValueError("Quantidade e estoque mínimo não podem ser negativos.")
    if not math.isfinite(produto.preco) or produto.preco < 0:
        raise ValueError("O preço deve ser um número válido e não negativo.")


class ListaSequencial:
    """Vetor dinâmico com busca sequencial: busca O(n)."""

    nome = "lista_sequencial"

    def __init__(self):
        self._itens = []

    def inserir(self, produto):
        self._itens.append(produto)

    def _indice(self, codigo):
        for indice in range(len(self._itens)):
            if self._itens[indice].codigo == codigo:
                return indice
        return -1

    def buscar(self, codigo):
        indice = self._indice(codigo)
        return self._itens[indice] if indice >= 0 else None

    def remover(self, codigo):
        indice = self._indice(codigo)
        if indice < 0:
            return False
        self._itens.pop(indice)
        return True

    def listar(self):
        return list(self._itens)

    def __len__(self):
        return len(self._itens)


class TabelaHash:
    """Tabela hash com encadeamento separado e redimensionamento."""

    nome = "tabela_hash"
    CAPACIDADE_INICIAL = 1009
    FATOR_CARGA_MAX = 0.75

    def __init__(self, capacidade=CAPACIDADE_INICIAL):
        self._capacidade = capacidade
        self._baldes = [[] for _ in range(capacidade)]
        self._quantidade = 0

    def _posicao(self, codigo):
        return codigo % self._capacidade

    def _redimensionar(self):
        antigos = self._baldes
        self._capacidade = self._capacidade * 2 + 1
        self._baldes = [[] for _ in range(self._capacidade)]
        for balde in antigos:
            for produto in balde:
                self._baldes[self._posicao(produto.codigo)].append(produto)

    def inserir(self, produto):
        if (self._quantidade + 1) / self._capacidade > self.FATOR_CARGA_MAX:
            self._redimensionar()
        self._baldes[self._posicao(produto.codigo)].append(produto)
        self._quantidade += 1

    def buscar(self, codigo):
        for produto in self._baldes[self._posicao(codigo)]:
            if produto.codigo == codigo:
                return produto
        return None

    def remover(self, codigo):
        balde = self._baldes[self._posicao(codigo)]
        for indice in range(len(balde)):
            if balde[indice].codigo == codigo:
                balde.pop(indice)
                self._quantidade -= 1
                return True
        return False

    def listar(self):
        return [produto for balde in self._baldes for produto in balde]

    def __len__(self):
        return self._quantidade


class DicionarioNativo:
    """Referência para comparar a hash manual com o dict nativo do Python."""

    nome = "dict_nativo"

    def __init__(self):
        self._itens = {}

    def inserir(self, produto):
        self._itens[produto.codigo] = produto

    def buscar(self, codigo):
        return self._itens.get(codigo)

    def remover(self, codigo):
        return self._itens.pop(codigo, None) is not None

    def listar(self):
        return list(self._itens.values())

    def __len__(self):
        return len(self._itens)


def merge_sort(itens, chave):
    """Merge Sort estável, O(n log n). Retorna uma nova lista ordenada."""
    if len(itens) <= 1:
        return list(itens)
    meio = len(itens) // 2
    esquerda = merge_sort(itens[:meio], chave)
    direita = merge_sort(itens[meio:], chave)
    resultado = []
    i = j = 0
    while i < len(esquerda) and j < len(direita):
        if chave(esquerda[i]) <= chave(direita[j]):
            resultado.append(esquerda[i])
            i += 1
        else:
            resultado.append(direita[j])
            j += 1
    resultado.extend(esquerda[i:])
    resultado.extend(direita[j:])
    return resultado


CRITERIOS_ORDENACAO = {
    "codigo": lambda produto: produto.codigo,
    "descricao": lambda produto: produto.descricao,
    "quantidade": lambda produto: produto.quantidade,
}


def carregar_csv(caminho, codigos_com_categoria=False):
    """Lê produtos do CSV e retorna uma lista de objetos Produto."""
    produtos = []
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        for linha in csv.DictReader(arquivo, delimiter=";"):
            codigo = linha["codigo"]
            produtos.append(Produto(
                codigo=interpretar_codigo(codigo) if codigos_com_categoria else int(codigo),
                descricao=linha["descricao"],
                quantidade=int(linha["quantidade"]),
                estoque_minimo=int(linha["estoque_minimo"]),
                preco=float(linha["preco"]),
            ))
    return produtos


def salvar_csv(caminho, produtos, codigos_com_categoria=False):
    Path(caminho).parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.writer(arquivo, delimiter=";")
        escritor.writerow(CAMPOS_CSV)
        for produto in produtos:
            codigo = formatar_codigo(produto.codigo) if codigos_com_categoria else produto.codigo
            escritor.writerow([
                codigo, produto.descricao, produto.quantidade,
                produto.estoque_minimo, f"{produto.preco:.2f}",
            ])


class Estoque:
    """Regras de negócio sobre uma estrutura de dados intercambiável."""

    def __init__(self, estrutura):
        self._estrutura = estrutura
        self._categorias = {}
        self._ultimo_numero = {}

    def __len__(self):
        return len(self._estrutura)

    def _obter(self, codigo):
        produto = self._estrutura.buscar(codigo)
        if produto is None:
            raise ValueError(f"Produto {formatar_codigo(codigo)} não encontrado.")
        return produto

    def cadastrar(self, produto):  # RF01
        """Cadastra produto com código definido, inclusive durante a carga."""
        validar_produto(produto)
        if self._estrutura.buscar(produto.codigo) is not None:
            raise ValueError(f"Já existe produto com o código {formatar_codigo(produto.codigo)}.")
        self._estrutura.inserir(produto)
        sigla = sigla_do_codigo(produto.codigo)
        self._ultimo_numero[sigla] = max(
            self._ultimo_numero.get(sigla, 0), produto.codigo % 1000
        )

    def buscar(self, codigo):  # RF02
        return self._estrutura.buscar(codigo)

    def alterar(self, codigo, descricao, estoque_minimo, preco):  # RF03
        atual = self._obter(codigo)
        descricao = descricao.strip()
        novo = Produto(codigo, descricao, atual.quantidade, estoque_minimo, preco)
        validar_produto(novo)
        atual.descricao = descricao
        atual.estoque_minimo = estoque_minimo
        atual.preco = preco

    def remover(self, codigo):  # RF04
        if not self._estrutura.remover(codigo):
            raise ValueError(f"Produto {formatar_codigo(codigo)} não encontrado.")

    def entrada(self, codigo, quantidade):  # RF05
        if quantidade <= 0:
            raise ValueError("A quantidade de entrada deve ser maior que zero.")
        self._obter(codigo).quantidade += quantidade

    def saida(self, codigo, quantidade):  # RF06
        if quantidade <= 0:
            raise ValueError("A quantidade de saída deve ser maior que zero.")
        produto = self._obter(codigo)
        if quantidade > produto.quantidade:
            raise ValueError(f"Estoque insuficiente: há {produto.quantidade} unidade(s).")
        produto.quantidade -= quantidade

    def listar_ordenado(self, criterio="codigo"):  # RF07
        return merge_sort(self._estrutura.listar(), CRITERIOS_ORDENACAO[criterio])

    def abaixo_do_minimo(self):  # RF08
        itens = [
            produto for produto in self._estrutura.listar()
            if produto.quantidade <= produto.estoque_minimo
        ]
        return merge_sort(itens, CRITERIOS_ORDENACAO["codigo"])

    def valor_total(self):  # RF09
        return sum(
            produto.quantidade * produto.preco
            for produto in self._estrutura.listar()
        )

    def carregar(self, caminho):  # RF10
        for produto in carregar_csv(caminho, codigos_com_categoria=True):
            self.cadastrar(produto)

    def salvar(self, caminho):  # RF10
        salvar_csv(caminho, self.listar_ordenado("codigo"), codigos_com_categoria=True)

    def cadastrar_categoria(self, sigla, nome):
        sigla = interpretar_sigla(sigla)
        nome = nome.strip()
        if not nome:
            raise ValueError("O nome da categoria é obrigatório.")
        if len(nome) > TAMANHO_MAX_NOME_CATEGORIA:
            raise ValueError(
                f"O nome da categoria deve ter até {TAMANHO_MAX_NOME_CATEGORIA} caracteres."
            )
        if ";" in nome or '"' in nome:
            raise ValueError("O nome da categoria não pode conter ';' nem aspas.")
        if sigla in self._categorias:
            raise ValueError(f"Já existe a categoria {sigla}.")
        self._categorias[sigla] = nome
        return sigla

    def usar_categorias_padrao(self):
        for sigla, nome in CATEGORIAS_PADRAO:
            self.cadastrar_categoria(sigla, nome)

    def categorias(self):
        """Lista (sigla, nome, quantidade de produtos), em ordem de sigla."""
        contagem = {}
        for produto in self._estrutura.listar():
            sigla = sigla_do_codigo(produto.codigo)
            contagem[sigla] = contagem.get(sigla, 0) + 1
        return [
            (sigla, self._categorias[sigla], contagem.get(sigla, 0))
            for sigla in sorted(self._categorias)
        ]

    def _exigir_categoria(self, sigla):
        sigla = interpretar_sigla(sigla)
        if sigla not in self._categorias:
            raise ValueError(f"Categoria {sigla} não cadastrada.")
        return sigla

    def _proximo_numero(self, sigla, quantidade):
        """Garante espaço para `quantidade` códigos sequenciais."""
        ultimo = self._ultimo_numero.get(sigla, 0)
        if ultimo + quantidade > NUMERO_MAXIMO:
            raise ValueError(
                f"A categoria {sigla} não tem códigos livres suficientes "
                f"(máximo {NUMERO_MAXIMO} itens)."
            )
        return ultimo + 1

    def cadastrar_na_categoria(self, sigla, descricao, quantidade, estoque_minimo, preco):
        """Cadastra com o próximo código livre da categoria."""
        sigla = self._exigir_categoria(sigla)
        codigo = montar_codigo(sigla, self._proximo_numero(sigla, 1))
        self.cadastrar(Produto(codigo, descricao.strip(), quantidade, estoque_minimo, preco))
        return codigo

    def carregar_categorias(self, caminho):
        with open(caminho, encoding="utf-8", newline="") as arquivo:
            for linha in csv.DictReader(arquivo, delimiter=";"):
                self.cadastrar_categoria(linha["sigla"], linha["nome"])

    def salvar_categorias(self, caminho):
        Path(caminho).parent.mkdir(parents=True, exist_ok=True)
        with open(caminho, "w", encoding="utf-8", newline="") as arquivo:
            escritor = csv.writer(arquivo, delimiter=";")
            escritor.writerow(CAMPOS_CATEGORIAS)
            for sigla in sorted(self._categorias):
                escritor.writerow([sigla, self._categorias[sigla]])

    def carregar_sequencias(self, caminho):
        """Carrega números já emitidos, preservando o maior valor por sigla."""
        with open(caminho, encoding="utf-8", newline="") as arquivo:
            for linha in csv.DictReader(arquivo, delimiter=";"):
                sigla = interpretar_sigla(linha["sigla"])
                try:
                    ultimo = int(linha["ultimo_numero"])
                except (TypeError, ValueError):
                    raise ValueError(f"Sequência inválida para a categoria {sigla}.")
                if not 0 <= ultimo <= NUMERO_MAXIMO:
                    raise ValueError(f"Sequência inválida para a categoria {sigla}.")
                self._ultimo_numero[sigla] = max(
                    self._ultimo_numero.get(sigla, 0), ultimo
                )

    def salvar_sequencias(self, caminho):
        """Grava marcas d'água independentes dos produtos ainda existentes."""
        Path(caminho).parent.mkdir(parents=True, exist_ok=True)
        with open(caminho, "w", encoding="utf-8", newline="") as arquivo:
            escritor = csv.writer(arquivo, delimiter=";")
            escritor.writerow(CAMPOS_SEQUENCIAS)
            for sigla in sorted(self._ultimo_numero):
                escritor.writerow([sigla, self._ultimo_numero[sigla]])

    def planejar_lote(self, sigla, descricao_base, tamanhos, quantidade, estoque_minimo, preco):
        """Monta e valida o lote sem cadastrar nenhum produto."""
        sigla = self._exigir_categoria(sigla)
        base = descricao_base.strip()
        if not base:
            raise ValueError("A descrição base é obrigatória.")
        lista = [tamanho.strip() for tamanho in tamanhos.split(",")]
        if lista == [""]:
            raise ValueError("Informe pelo menos um tamanho.")
        if "" in lista:
            raise ValueError("Tamanho vazio na lista.")
        if len(lista) > MAXIMO_TAMANHOS_LOTE:
            raise ValueError(f"Máximo de {MAXIMO_TAMANHOS_LOTE} tamanhos por lote.")
        vistos = set()
        for tamanho in lista:
            if tamanho in vistos:
                raise ValueError(f"Tamanho repetido: {tamanho}.")
            vistos.add(tamanho)
        primeiro = self._proximo_numero(sigla, len(lista))
        produtos = []
        for indice, tamanho in enumerate(lista):
            produto = Produto(
                montar_codigo(sigla, primeiro + indice),
                f"{base} tam {tamanho}", quantidade, estoque_minimo, preco,
            )
            validar_produto(produto)
            produtos.append(produto)
        return produtos

    def cadastrar_lote(self, produtos):
        """Confere todos os produtos antes de inserir o primeiro."""
        for produto in produtos:
            validar_produto(produto)
            if self._estrutura.buscar(produto.codigo) is not None:
                raise ValueError(
                    f"Já existe produto com o código {formatar_codigo(produto.codigo)}."
                )
        for produto in produtos:
            self.cadastrar(produto)

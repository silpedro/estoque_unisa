"""Frontend de console; as regras e estruturas ficam no modulo estoque (backend)."""

from pathlib import Path

from estoque import Estoque, TabelaHash, formatar_codigo, interpretar_codigo

PASTA_DADOS = Path(__file__).resolve().parent / "dados"
ARQUIVO_ESTOQUE = PASTA_DADOS / "estoque.csv"
ARQUIVO_CATEGORIAS = PASTA_DADOS / "categorias.csv"
ARQUIVO_SEQUENCIAS = PASTA_DADOS / "sequencias.csv"

# Margem à esquerda de todas as telas (ajuste aqui para mudar o recuo).
MARGEM = " " * 4


def exibir(texto=""):
    """Como print(), mas com margem no início de cada linha."""
    for linha in str(texto).split("\n"):
        print(MARGEM + linha if linha else "")


def perguntar(mensagem):
    """Como input(), mas com margem antes da pergunta."""
    return input(MARGEM + mensagem)


BANNER = """
        ________________________
       /                       /|
      /_______________________/ |
      | | | | | | | | ._____. | |
      | | | | | | | | |  |  | | |
      | | | | | | | | |  |  | | /
      |_|_|_|_|_|_|_|_|__|__|_|/
          CONTROLE DE ESTOQUE
"""

CREDITOS = """             Desenvolvido por Pedro Paulo
     Engenharia de Software - 4º semestre"""

MENU = """
========== CONTROLE DE ESTOQUE ==========
 1 - Cadastrar produto
 2 - Buscar produto
 3 - Alterar produto
 4 - Remover produto
 5 - Registrar entrada
 6 - Registrar saída
 7 - Listar produtos
 8 - Produtos para repor (abaixo do mínimo)
 9 - Valor total do estoque
10 - Cadastrar categoria
11 - Listar categorias
12 - Cadastrar em lote (grade de tamanhos)
13 - Salvar
 0 - Sair
========================================="""


def ler_inteiro(mensagem):
    while True:
        try:
            return int(perguntar(mensagem))
        except ValueError:
            exibir("Digite um número inteiro.")


def ler_real(mensagem):
    while True:
        try:
            return float(perguntar(mensagem).replace(",", "."))
        except ValueError:
            exibir("Digite um número (ex.: 12,50).")


def ler_codigo(mensagem="Código (ex.: UV001): "):
    return interpretar_codigo(perguntar(mensagem))


def formatar_moeda(valor):
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def imprimir_tabela(produtos):
    if not produtos:
        exibir("Nenhum produto.")
        return
    exibir(f"{'CÓDIGO':>8}  {'DESCRIÇÃO':<50}  {'QTD':>6}  {'MÍN':>6}  {'PREÇO':>12}")
    for produto in produtos:
        exibir(
            f"{formatar_codigo(produto.codigo):>8}  {produto.descricao:<50}  "
            f"{produto.quantidade:>6}  {produto.estoque_minimo:>6}  "
            f"{formatar_moeda(produto.preco):>12}"
        )
    exibir(f"Total: {len(produtos)} produto(s).")


def mostrar_categorias_disponiveis(estoque):
    """Lista as siglas disponíveis ou avisa que nenhuma categoria existe."""
    categorias = estoque.categorias()
    if not categorias:
        exibir("Erro: Nenhuma categoria cadastrada. Cadastre uma pela opção 10.")
        return False
    exibir("Categorias disponíveis:")
    for sigla, nome, _ in categorias:
        exibir(f"  {sigla} - {nome}")
    return True


def cadastrar(estoque):
    if not mostrar_categorias_disponiveis(estoque):
        return False
    sigla = perguntar("Categoria (sigla): ")
    descricao = perguntar("Descrição: ")
    quantidade = ler_inteiro("Quantidade inicial: ")
    minimo = ler_inteiro("Estoque mínimo: ")
    preco = ler_real("Preço unitário: ")
    codigo = estoque.cadastrar_na_categoria(sigla, descricao, quantidade, minimo, preco)
    exibir(f"Produto cadastrado com o código {formatar_codigo(codigo)}.")
    return True


def buscar(estoque):
    produto = estoque.buscar(ler_codigo())
    imprimir_tabela([produto] if produto else [])
    return False


def alterar(estoque):
    codigo = ler_codigo()
    if estoque.buscar(codigo) is None:
        raise ValueError(f"Produto {formatar_codigo(codigo)} não encontrado.")
    estoque.alterar(
        codigo,
        perguntar("Nova descrição: "),
        ler_inteiro("Novo estoque mínimo: "),
        ler_real("Novo preço: "),
    )
    exibir("Produto alterado.")
    return True


def remover(estoque):
    estoque.remover(ler_codigo())
    exibir("Produto removido.")
    return True


def entrada(estoque):
    codigo = ler_codigo()
    estoque.entrada(codigo, ler_inteiro("Quantidade: "))
    exibir("Entrada registrada.")
    return True


def saida(estoque):
    codigo = ler_codigo()
    estoque.saida(codigo, ler_inteiro("Quantidade: "))
    exibir("Saída registrada.")
    return True


def listar(estoque):
    exibir("Ordenar por: 1 - código  2 - descrição  3 - quantidade")
    criterio = {
        1: "codigo", 2: "descricao", 3: "quantidade"
    }.get(ler_inteiro("Opção: "), "codigo")
    imprimir_tabela(estoque.listar_ordenado(criterio))
    return False


def repor(estoque):
    imprimir_tabela(estoque.abaixo_do_minimo())
    return False


def valor_total(estoque):
    exibir(f"Valor total do estoque: {formatar_moeda(estoque.valor_total())}")
    return False


def gravar_arquivos(estoque):
    # A marca d'água é gravada primeiro: uma falha posterior pode pular um
    # número, mas nunca permite reutilizar um código já emitido.
    estoque.salvar_sequencias(ARQUIVO_SEQUENCIAS)
    estoque.salvar(ARQUIVO_ESTOQUE)
    estoque.salvar_categorias(ARQUIVO_CATEGORIAS)


def salvar(estoque):
    gravar_arquivos(estoque)
    exibir(f"Estoque salvo em {ARQUIVO_ESTOQUE}.")
    return False


def cadastrar_categoria(estoque):
    sigla = perguntar("Sigla (2 letras): ")
    nome = perguntar("Nome da categoria: ")
    sigla = estoque.cadastrar_categoria(sigla, nome)
    exibir(f"Categoria {sigla} cadastrada.")
    return True


def listar_categorias(estoque):
    categorias = estoque.categorias()
    if not categorias:
        exibir("Nenhuma categoria.")
        return False
    exibir(f"{'SIGLA':<5}  {'NOME':<40}  {'ITENS':>5}")
    for sigla, nome, itens in categorias:
        exibir(f"{sigla:<5}  {nome:<40}  {itens:>5}")
    exibir(f"Total: {len(categorias)} categoria(s).")
    return False


def cadastrar_lote(estoque):
    if not mostrar_categorias_disponiveis(estoque):
        return False
    sigla = perguntar("Categoria (sigla): ")
    base = perguntar("Descrição base: ")
    tamanhos = perguntar("Tamanhos (separados por vírgula): ")
    quantidade = ler_inteiro("Quantidade inicial de cada: ")
    minimo = ler_inteiro("Estoque mínimo de cada: ")
    preco = ler_real("Preço unitário: ")
    plano = estoque.planejar_lote(sigla, base, tamanhos, quantidade, minimo, preco)
    exibir(f"Serão cadastrados {len(plano)} produto(s):")
    for produto in plano:
        exibir(f"  {formatar_codigo(produto.codigo)}  {produto.descricao}")
    if perguntar("Confirmar? (S/N): ").strip().upper() != "S":
        exibir("Cadastro em lote cancelado.")
        return False
    estoque.cadastrar_lote(plano)
    exibir(
        f"{len(plano)} produto(s) cadastrado(s), de "
        f"{formatar_codigo(plano[0].codigo)} a {formatar_codigo(plano[-1].codigo)}."
    )
    return True


ACOES = {
    1: cadastrar, 2: buscar, 3: alterar, 4: remover, 5: entrada,
    6: saida, 7: listar, 8: repor, 9: valor_total,
    10: cadastrar_categoria, 11: listar_categorias, 12: cadastrar_lote,
    13: salvar,
}


def salvar_automaticamente(estoque):
    try:
        gravar_arquivos(estoque)
        exibir("(alteração salva automaticamente)")
    except OSError as erro:
        exibir(
            f"Erro: não foi possível salvar o arquivo ({erro}). "
            "Use a opção 13 para tentar de novo."
        )


def main():
    exibir(BANNER)
    exibir(CREDITOS)
    estoque = Estoque(TabelaHash())
    if ARQUIVO_CATEGORIAS.exists():
        estoque.carregar_categorias(ARQUIVO_CATEGORIAS)
    else:
        estoque.usar_categorias_padrao()
    if ARQUIVO_SEQUENCIAS.exists():
        estoque.carregar_sequencias(ARQUIVO_SEQUENCIAS)
    if ARQUIVO_ESTOQUE.exists():
        estoque.carregar(ARQUIVO_ESTOQUE)
        exibir(f"{len(estoque)} produto(s) carregado(s) de {ARQUIVO_ESTOQUE}.")

    try:
        while True:
            exibir(MENU)
            opcao = ler_inteiro("Opção: ")
            if opcao == 0:
                salvar(estoque)
                break
            acao = ACOES.get(opcao)
            if acao is None:
                exibir("Opção inválida.")
                continue
            try:
                alterou = acao(estoque)
            except ValueError as erro:
                exibir(f"Erro: {erro}")
                continue
            if alterou:
                salvar_automaticamente(estoque)
    except (KeyboardInterrupt, EOFError):
        exibir("\nPrograma encerrado.")


if __name__ == "__main__":
    main()

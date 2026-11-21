# Controle de Estoque — `estoque_unisa`

Aplicação de console em Python para cadastrar produtos, controlar movimentações de
estoque e acompanhar itens que precisam de reposição. Este repositório é uma base
privada de testes do sistema; não inclui os documentos acadêmicos nem os dados de
demonstração do projeto de referência.

## Funcionalidades

- Cadastro de categorias e produtos com código sequencial por categoria, como `UV001`.
- Busca, alteração e remoção de produtos.
- Registro de entradas e saídas, sem permitir saldo negativo.
- Listagens ordenadas por código, descrição ou quantidade.
- Relatório de produtos com quantidade menor ou igual ao estoque mínimo.
- Cálculo do valor total do estoque.
- Cadastro em lote de uma grade de tamanhos, com prévia, confirmação e validação
  integral antes de inserir os produtos.
- Salvamento automático das alterações bem-sucedidas.

## Organização do código

O programa separa a interface das regras e estruturas:

| Arquivo | Responsabilidade |
|---|---|
| `main.py` | Interface de console: banner, menu, entrada e saída de informações. |
| `estoque.py` | Backend: produto, validações, estruturas de dados, regras de negócio e persistência CSV. |

O menu utiliza a tabela hash implementada no backend. A lista sequencial e o Merge
Sort também são implementados manualmente; `DicionarioNativo` existe como referência
para comparação de estrutura.

## Requisitos e execução

- Python 3.12 ou superior.
- Somente biblioteca padrão do Python; não é necessário instalar dependências.

Na pasta do repositório, execute:

```powershell
python main.py
```

O menu oferece as opções numeradas de cadastro a salvamento. Use `0` para salvar e
sair; a opção `13` salva sem encerrar o programa.

As categorias iniciais são `EP` (Equipamento de Protecao Individual) e `UV`
(Uniforme e Vestimenta). Categorias adicionais podem ser cadastradas pelo menu.

## Arquivos de dados

Os CSVs são criados na subpasta `dados`, ao lado de `main.py`:

| Arquivo | Conteúdo |
|---|---|
| `dados/estoque.csv` | Produtos e saldos atuais. |
| `dados/categorias.csv` | Siglas e nomes das categorias. |
| `dados/sequencias.csv` | Maior número já emitido por categoria, inclusive para códigos removidos. |

Os arquivos usam UTF-8, `;` como separador e ponto decimal para preços. O sistema
grava os arquivos após cada operação bem-sucedida que altera o estoque ou as
categorias, além de salvar ao sair.

Exemplo de cabeçalho do estoque:

```text
codigo;descricao;quantidade;estoque_minimo;preco
UV001;CAMISETA SOCIAL;10;2;49.90
```

Cada categoria aceita até 999 códigos (`AA001` a `AA999`), para um máximo teórico de
676 siglas e 675.324 produtos. A numeração não é reutilizada após remoções. Ao
carregar dados antigos sem `sequencias.csv`, o sistema recupera o maior código ainda
presente no estoque; não é possível inferir números que já tinham sido removidos
antes da criação do arquivo de sequências.

Nenhum estoque pessoal ou catálogo de demonstração foi copiado para este repositório.
Na primeira execução, o estoque começa vazio e as categorias padrão são carregadas
em memória.

## Validação e escopo

Durante o desenvolvimento, a aplicação passou pelos 25 testes da suíte de referência
e por dois testes adicionais para a persistência de códigos e o salvamento automático.
A suíte de testes não está incluída neste repositório; por isso, esses testes não
podem ser executados diretamente daqui.

Este repositório contém a aplicação de console, mas não inclui os scripts de benchmark,
massas de dados experimentais, resultados acadêmicos ou figuras do projeto de
referência. Os tempos publicados na documentação desse projeto não são medições
geradas por este repositório.

import spacy

# SetUp
nlp = spacy.load("pt_core_news_lg")


def verboHTTPPorSimilaridade(verboentrada):
    print()
    gruposBase = [("GET", "consultar buscar pesquisar"), ("POST", "inserir cadastrar criar"),
                  ("DELETE", "deletar apagar excluir"), ("PUT", "alterar modificar atualizar")]

    similaridadeGrupo = []
    grupo = 0
    for grupoBase in gruposBase:
        tokensbase = [token for token in nlp(grupoBase[1])]
        docentrada = nlp(verboentrada)
        valorgrupo = 0
        for tokenbase in tokensbase:
            valorgrupo = valorgrupo + tokenbase.similarity(docentrada)
        similaridadeGrupo.insert(grupo, (grupoBase[0], valorgrupo / 3))
        grupo = grupo + 1

    indiceDoMaiorValor = -1
    maiorValor = 0
    indice = 0
    for grupoBase in gruposBase:
        if similaridadeGrupo[indice][1] > maiorValor:
            maiorValor = similaridadeGrupo[indice][1]
            indiceDoMaiorValor = indice
        indice = indice + 1

    print(similaridadeGrupo[indiceDoMaiorValor])


verboHTTPPorSimilaridade("cadastro")
verboHTTPPorSimilaridade("consultar")
verboHTTPPorSimilaridade("buscar")
verboHTTPPorSimilaridade("pesquisar")
verboHTTPPorSimilaridade("inserir")
verboHTTPPorSimilaridade("criar")
verboHTTPPorSimilaridade("cadastrar")
verboHTTPPorSimilaridade("deletar")
verboHTTPPorSimilaridade("excluir")
verboHTTPPorSimilaridade("apagar")
verboHTTPPorSimilaridade("mudar")
verboHTTPPorSimilaridade("atualizar")
verboHTTPPorSimilaridade("alterar")

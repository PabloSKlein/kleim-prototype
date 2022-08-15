import spacy
import codecs

reservadasGherkin = ["funcionalidade", "cenario", "quando", "entao", "e", "contexto"]

codigoInicioClasse = "import io.cucumber.java.pt.*;" + \
                     "\nimport io.restassured.response.Response;" + \
                     "\nimport org.hamcrest.Matchers;" + \
                     "\nimport static io.restassured.RestAssured.given;" + \
                     "\n" + \
                     "\npublic class PessoasSteps {" + \
                     "\n    private Response response;" + \
                     "\n"

codigoContextoURL = "\n    private static final String URL = {0}; \n"

codigoInicioMetodo = "\n    @Quando(\" {0} \") " + \
                     "\n    public void euPesquisarAPessoaDeDocumento( {1} ) "
codigoFimMetodo = "\n    }"
codigoFimClasse = "\n}"


def verbohttpporsimilaridade(verboentrada):
    gruposBase = [("GET", "consultar buscar pesquisar pesquisa", 4), ("POST", "inserir cadastrar criar gravar", 4),
                  ("DELETE", "deletar apagar excluir", 3), ("PUT", "alterar modificar atualizar", 4)]

    similaridadeGrupo = []
    grupo = 0
    for grupoBase in gruposBase:
        tokensbase = [token for token in nlp(grupoBase[1])]
        docentrada = nlp(verboentrada)
        valorgrupo = 0
        for tokenbase in tokensbase:
            valorgrupo = valorgrupo + tokenbase.similarity(docentrada)
        similaridadeGrupo.insert(grupo, (grupoBase[0], valorgrupo / grupoBase[2]))
        grupo = grupo + 1

    indiceDoMaiorValor = -1
    maiorValor = 0
    indice = 0
    for grupoBase in gruposBase:
        if similaridadeGrupo[indice][1] > maiorValor:
            maiorValor = similaridadeGrupo[indice][1]
            indiceDoMaiorValor = indice
        indice = indice + 1
    return similaridadeGrupo[indiceDoMaiorValor]


def removestopwordstexto(frase):
    frasesemstopword1 = ""
    for token in frase.split():
        if not token.startswith("\""):  # token.lower() not in stopwords and
            frasesemstopword1 = frasesemstopword1 + " " + token.lower()
    return frasesemstopword1


def getparametros(frase, metodo):
    parametros = ""
    if metodo == "GET":
        palavras = []
        for token in frase.split():
            if token.startswith("\""):
                palavras.append(token)
        i = 0
        while i < len(palavras):
            parametros += palavras[i].lower().replace("\"", "") + ", " + palavras[i].lower().replace("\"",
                                                                                                     "") + "Valor, "
            i += 2

        return parametros[:-2]
    else:
        if metodo == "POST":
            return getparametrosComoJson(frase)


def getnomeParametro(frase):
    nomeParametrosString = ""
    parametros = []

    for token in frase.split():
        if token.startswith("\""):
            parametros.append(token)

    i = 0
    while i < len(parametros):
        nomeParametrosString += " String {0}, String {0}Valor,".format(parametros[i])
        i += 2

    return nomeParametrosString[:-1].replace("\"", "")


def getparametrosComoJson(frase):
    jsonFormat = " \" + {0} + \": \" + {1} + \","
    parametrosString = "\"{ "
    parametros = []

    for token in frase.split():
        if token.startswith("\""):
            parametros.append(token)

    i = 0
    while i < len(parametros):
        parametrosString += jsonFormat.format(parametros[i].replace("\"", ""),
                                              parametros[i].lower().replace("\"", "") + "Valor")
        i += 2

    return parametrosString[:-1] + "}\""


def obtemverboseauxiliares(frase):
    verboseauxiliares1 = []
    print(frase)
    for token in frase:
        if token.pos_ == "VERB" or token.pos_ == "NOUN":
            verboseauxiliares1.append(token)
    return verboseauxiliares1


def processacontexto(linha):
    codigo = codigoInicioClasse
    for token in linha.split():
        if token.startswith("\""):
            codigo += codigoContextoURL.format(token)
    return codigo


def processaquando(linha):
    # Processamento
    fraseSemStopWord = removestopwordstexto(linha)

    fraseTokenizada = nlp(fraseSemStopWord)

    verbosEAuxiliares = obtemverboseauxiliares(fraseTokenizada)
    print(verbosEAuxiliares)

    listaDeSimilaridades = []
    for palavra in verbosEAuxiliares:
        listaDeSimilaridades.append(verbohttpporsimilaridade(palavra.text))
    print(listaDeSimilaridades)

    maior = ("None", 0)
    for similaridade in listaDeSimilaridades:
        if similaridade[1] > maior[1]:
            maior = similaridade
    print(maior)

    linhaParaNotacao = ""
    for token in linha.split()[1:]:
        if token.startswith("\""):
            linhaParaNotacao += "{string} "
        else:
            linhaParaNotacao += token.lower() + " "

    for codigo in codigos:
        if codigo[0] == maior[0]:
            return codigoInicioMetodo.format(linhaParaNotacao, getnomeParametro(linha)) + "{\n        " \
                   + codigo[1].format(getparametros(linha, codigo[0])) + codigoFimMetodo


def getCodigoLinha(linha):
    codigoLinha = ""
    if linha.split()[0].lower() == "quando":
        return processaquando(linha)
    elif linha.split()[0].lower() == "contexto":
        return processacontexto(linha)
    print(codigoLinha)


# SetUp
codigos = [("GET", "response = given().param({0}).when().get(URL);"),
           ("POST", "response = given().when().body({0}).post(URL);"),
           ("DELETE", "response = given().when().body({0}).patch(URL);"),
           ("PATCH", "response = given().when().body({0}).delete(URL);")]


nlp = spacy.load("pt_core_news_lg")

texto = "#language: pt \n" \
        "Funcionalidade: Crud de Pessoas \n\n" \
        "Contexto Utilizando o serviço \"http://localhost:8080/pessoas\" \n" \
        "Cenario: Pesquisa de uma pessoa " \
        "Quando Eu pesquisar a pessoa de \"documento\" \"04000440444\" \n"

linha0 = "Contexto Utilizando o serviço \"http://localhost:8080/pessoas\""
linha = "Quando Eu gravar uma nova pessoa de \"documento\" \"04000440444\" e \"nome\" \"Pablo\""
# linha = "Quando Eu pesquisar uma pessoa pelo número de \"documento\" \"04000440444\""

codigoCompleto = ""
codigoCompleto += getCodigoLinha(linha0)
codigoCompleto += getCodigoLinha(linha)

with codecs.open('Steps.java', 'w', 'utf-8') as f:
    f.write(codigoCompleto + codigoFimClasse)

# tokensFrase = [tok.orth_ for tok in fraseTokenizada]

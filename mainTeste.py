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
                     "\n    public void {1}( {2} ) "
codigoInicioMetodoEntao = "\n    @{0}(\" {1} \") " + \
                          "\n    public void {2}( {3} ) "
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
        if not token.startswith("\"") and not token.endswith("\""):  # token.lower() not in stopwords and
            frasesemstopword1 += " " + token.lower()

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
            parametro = palavras[i].lower().replace("\"", "")
            parametros += parametro + ", " + parametro + "Valor, "
            i += 2

        return parametros[:-2]
    elif metodo == "POST":
        return getparametrosComoJson(frase)
    else:
        return ""


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
        parametro = parametros[i].lower().replace("\"", "")
        parametrosString += jsonFormat.format(parametro, parametro + "Valor")
        i += 2

    return parametrosString[:-1] + "}\""


def obtemverboseauxiliares(frase):
    verboseauxiliares1 = []
    print(frase)
    for token in frase:
        if token.pos_ == "VERB" or token.pos_ == "NOUN":
            verboseauxiliares1.append(token)
    return verboseauxiliares1


def processaentao(linha):
    parametros = []
    parametros2 = []
    parametros3 = []

    fraseSemStopWord = removestopwordstexto(linha)

    fraseTokenizada = nlp(fraseSemStopWord)
    fraseCompletaTokenizada = nlp(linha.replace("\"", ""))
    verboGherkin = fraseTokenizada[1].text.capitalize()
    for token in fraseTokenizada[1:]:
        if token.pos_ == "NOUN":  # or token.pos_ == "ADJ"
            parametros3.append(token.text)
            parametros.append(token.text)

    codigo = ""

    print(linha)
    for palavra in linha.split():
        if palavra.startswith("\"") or palavra.isnumeric():
            parametros2.append(palavra)
            parametros.append(palavra)

    nomeNotacao = ""
    for palavra in linha.split()[1:]:
        if palavra.startswith("\""):
            nomeNotacao += "{string} "
        elif palavra.isnumeric():
            nomeNotacao += "{int} "
        else:
            nomeNotacao += palavra + " "

    nomeMetodo = parametros[0]
    for parametro in parametros[1:]:
        nomeMetodo += parametro.replace("\"", "").capitalize()

    nomeParametro = ""
    if len(parametros2) == 1:
        if parametros2[0].startswith("\""):
            nomeParametro += "String " + parametros3[0]
        else:
            nomeParametro += "int " + parametros3[0]
        codigo = codigosEntao[0][1].format(parametros3[0])
    else:
        i = 0
        while i < len(parametros):
            if parametros[i].startswith("\""):
                comparacao = getMatcher(fraseCompletaTokenizada)

                parametro = parametros[i].replace("\"", "")
                nomeParametro += "String {0}, String {1}".format(parametro, parametro + "Valor ")
                codigo += codigosEntao[1][1].format(parametro, comparacao, parametro) + "\n"
                i += 1
            elif parametros[i].isnumeric():
                comparacao = getMatcher(fraseCompletaTokenizada)

                parametro = parametros[i].replace("\"", "")
                nomeParametro += "String {0}, int {1}".format(parametro, parametro + "Valor")
                codigo += codigosEntao[1][1].format(parametro, comparacao, parametro) + "\n"
                i += 1
            i += 1

    print(parametros)

    #print(nlp("body").similarity(nlp("corpo")))
    return codigoInicioMetodoEntao.format(verboGherkin, nomeNotacao, nomeMetodo, nomeParametro) + "{\n        " + codigo + codigoFimMetodo


def getMatcher(fraseCompletaTokenizada):
    comparacao = ""
    for token in fraseCompletaTokenizada[1:]:
        if token.pos_ == "ADJ":  # or token.pos_ == "ADJ"
            comparacao = token.text
    if comparacao == "":
        return codigosMatcher[0][1]

    # codigo - ValorSimiliaridade
    maior = ("None", 0)
    for matcher in codigosMatcher:
        similaridade = nlp(matcher[0]).similarity(nlp(comparacao))
        if similaridade > maior[1]:
            maior = [matcher[1], similaridade]
    print(maior)
    return maior[0]


def processacontexto(linha):
    codigo = codigoInicioClasse
    for token in linha.split():
        if token.startswith("\""):
            codigo += codigoContextoURL.format(token)
    return codigo


def getNomeMetodo(verbosEAuxiliares, linha):
    verbos = verbosEAuxiliares[0].text
    for verbo in verbosEAuxiliares[1:]:
        verbos += verbo.text.capitalize()

    parametros = []
    for token in linha.split():
        if token.startswith("\""):
            parametros.append(token.replace("\"", ""))
    i = 0
    while i < len(parametros):
        verbos += parametros[i].capitalize()
        i += 2

    return verbos


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
        elif token.endswith("\""):
            linhaParaNotacao += ""
        else:
            linhaParaNotacao += token.lower() + " "

    for codigo in codigos:
        if codigo[0] == maior[0]:
            return codigoInicioMetodo.format(linhaParaNotacao, getNomeMetodo(verbosEAuxiliares, linha),
                                             getnomeParametro(linha)) + "{\n        " \
                   + codigo[1].format(getparametros(linha, codigo[0])) + codigoFimMetodo


def getCodigoLinha(linha):
    verboGherkin = linha.split()[0].lower()
    if verboGherkin == "quando":
        return processaquando(linha)
    elif verboGherkin == "contexto":
        return processacontexto(linha)
    elif verboGherkin == "entao" or verboGherkin == "e":
        return processaentao(linha)
    return ""


# SetUp
codigos = [("GET", "response = given().param({0}).when().get(URL);"),
           ("POST", "response = given().when().body({0}).post(URL);"),
           ("DELETE", "response = given().when().body({0}).patch(URL);"),
           ("PATCH", "response = given().when().body({0}).delete(URL);")]

codigosEntao = [("status", "response.then().statusCode({0});"),
                ("bodyEqual", "response.then().body({0}, {1}({2}));")]
codigosMatcher = [("igual", "Matchers.equalTo"),
                  ("maior", "Matchers.graterThan"),
                  ("nao nulo", "notNullValue")]

nlp = spacy.load("pt_core_news_lg")

texto = "#language: pt \n" \
        "Funcionalidade: Crud de Pessoas \n" \
        "Contexto Utilizando o serviço \"http://localhost:8080/pessoas\" \n" \
        "Cenario: Pesquisa de uma pessoa \n" \
        "Quando Eu gravar uma pessoa com \"documento\" \"04000440444\" e \"nome\" \"Pablo Kleim\" \n" \
        "Entao deve ser retornado uma pessoa de \"nome\" igual a \"pablo\" \n"

codigoCompleto = ""
for linha in texto.splitlines():
    codigoCompleto += getCodigoLinha(linha)

# linha0 = "Contexto Utilizando o serviço \"http://localhost:8080/pessoas\""
# linha = "Quando Eu gravar uma nova pessoa de \"documento\" \"04000440444\" e \"nome\" \"Pablo\""
# linha = "Quando Eu pesquisar uma pessoa pelo número de \"documento\" \"04000440444\""

with codecs.open('Steps.java', 'w', 'utf-8') as f:
    f.write(codigoCompleto + codigoFimClasse)

# tokensFrase = [tok.orth_ for tok in fraseTokenizada]

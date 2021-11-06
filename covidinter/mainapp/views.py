from random import randint

from django.shortcuts import render
from django.views.generic import View
from django.contrib.staticfiles.storage import staticfiles_storage
import csv
import datetime
from django.http import HttpResponse


# Create your views here.
def pega_nome_colunas_csv():
    path = staticfiles_storage.path('mainapp/InternationalCovid19Cases.csv')
    arquivo = open(path)
    csvreader = csv.reader(arquivo)

    header = next(csvreader)
    arquivo.close()
    return header


class MainPage(View):
    # Limita quais campos podem ser buscado no formulario
    tipos_ordenacao = ['Novos Casos', 'Total de Casos', 'Novas Mortes', 'Total de Mortes']
    ordenacao_selecionada = None
    colunas = pega_nome_colunas_csv()

    def post(self, request):
        context = {'tipos_ordenacao': self.tipos_ordenacao, 'ordenacao_selecionada': self.ordenacao_selecionada}
        for envio in request.POST:
            if envio == 'ordenar':
                lista, valor, tempos = realiza_ordenacao(request.POST['ordenar'])
                self.ordenacao_selecionada = request.POST['ordenar']
                request.session['lista'] = lista
                request.session['valor'] = valor
                request.session['tempos'] = tempos
                context = {'tipos_ordenacao': self.tipos_ordenacao, 'tempos': tempos,
                           'ordenacao_selecionada': self.ordenacao_selecionada, 'colunas': self.colunas}
            elif envio == 'buscar':
                tempos = request.session['tempos']
                dados_busca = realiza_busca(request.session['lista'], request.session['valor'], request.POST['buscar'])

                if tempos:
                    context = {'tipos_ordenacao': self.tipos_ordenacao, 'dados_busca': dados_busca, 'tempos': tempos,
                               'ordenacao_selecionada': self.ordenacao_selecionada, 'colunas': self.colunas,'busca':request.POST['buscar']}
                else:
                    context = {'tipos_ordenacao': self.tipos_ordenacao, 'dados_busca': dados_busca,
                               'ordenacao_selecionada': self.ordenacao_selecionada, 'colunas': self.colunas,'busca':request.POST['buscar']}
        return render(request, 'mainapp/page.html', context)

    def get(self, request):

        context = {'tipos_ordenacao': self.tipos_ordenacao}
        return render(request, 'mainapp/page.html', context)


# Utilizado busca liner devido a possibilidade de elementos repetidos
def realiza_busca(listas, index, busca=None):
    resultados = []
    if busca:  # Se encontrar chave para ser buscado encontra
        for x in range(len(listas)):
            if float(listas[x][index]) == int(busca):
                resultados.append(listas[x])
    else:  # Caso não encontre, significa buscar um valor aleatório para fazer o teste de tempo em geraTemposExecucao
        aleatorio = randint(0, len(listas))
        for x in range(len(listas)):
            if float(listas[x][index]) == float(listas[aleatorio][index]):
                resultados.append(listas[x])

    return resultados


# Faz a 'mesclagem' das arrays esqueda/direita as ordenando
def mergeArray(esq, dir, indexDados):
    final = []
    aux, aux2 = 0, 0
    # Realizar comparação dos valores e determina ordem que será adicionado no final
    while aux < len(esq) and aux2 < len(dir):
        if esq[aux][indexDados] <= dir[aux2][indexDados]:
            final.append(esq[aux])
            aux += 1
        else:
            final.append(dir[aux2])
            aux2 += 1

    final += esq[aux:]
    final += dir[aux2:]
    return final


def mergesort(vetor, indexDados):
    if (len(vetor) <= 1):  # ordenado
        return vetor
    centro = int(len(vetor) / 2)
    # separação esqueda
    esq = mergesort(vetor[:centro], indexDados)
    # separação direita
    dir = mergesort(vetor[centro:], indexDados)

    return mergeArray(esq, dir, indexDados)


# Ordenação por Merge Sort
# tipo = tipo da ordenação selecionada pelo usuário, Buscar por Mortes, Quantidades de casos ...
def realiza_ordenacao(tipo):
    linhas, index = extrair_dados_csv(tipo)

    # Teste em minimundo
    # linhasteste = [[1, 8], [2, 4], [3, 1], [4, 5], [5, 2], [6, 7], [7, 9], [8, 3], ]
    linhas = mergesort(linhas, index)
    tempos = geraTemposExecucao(linhas, index)

    return linhas, index, tempos


def geraTemposExecucao(linhas, index):
    # linhasteste = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    # centro = len(linhasteste) / 2
    # pf = linhasteste[:int(centro)]
    # sf = linhasteste[int(centro):]
    # print(sf + pf)

    melhor_tempo = []
    pior_tempo = []
    medio_tempo = []
    # Execução medio caso
    for x in range(4):
        start = datetime.datetime.now()
        linhasMedio = mergesort(linhas, index)
        realiza_busca(linhasMedio, index)
        fim = datetime.datetime.now()
        medio_tempo.append(fim - start)

    # Melhor caso
    for x in range(3):
        start = datetime.datetime.now()
        linhasMelhor = mergesort(linhasMedio, index)
        realiza_busca(linhasMelhor, index)
        fim = datetime.datetime.now()
        melhor_tempo.append(str(fim - start))

    # Gera lista para execução do pior caso
    centro = len(melhor_tempo) / 2
    primeiraFatia = linhasMelhor[:int(centro)]
    segundaFatia = linhasMelhor[int(centro):]
    linhasParaPior = segundaFatia + primeiraFatia
    # Pior Caso
    for x in range(3):
        start = datetime.datetime.now()
        linhasPior = mergesort(linhasParaPior, index)
        realiza_busca(linhasPior, index)
        fim = datetime.datetime.now()
        pior_tempo.append(str(fim - start))

    soma = medio_tempo[0] + medio_tempo[1] + medio_tempo[2] + medio_tempo[3]

    media = soma / len(medio_tempo)
    return ["Melhor Caso: %s" % str(min(melhor_tempo)), "Médio Caso: %s" % str(media),
            "Pior Caso: %s" % str(max(pior_tempo))]


def extrair_dados_csv(tipo):
    linhas = []  # Armazena as linhas do csv
    if tipo == 'Novos Casos':
        tipo = 'new_cases'
    elif tipo == 'Total de Casos':
        tipo = 'total_cases'
    elif tipo == 'Novas Mortes':
        tipo = 'new_deaths'
    elif tipo == 'Total de Mortes':
        tipo = 'total_deaths'

    # Leitura do arquivo
    path = staticfiles_storage.path('mainapp/InternationalCovid19Cases.csv')
    arquivo = open(path)
    csvreader = csv.reader(arquivo)

    header = next(csvreader).index(tipo)  # Armazena o index da coluna que será utilizada

    for linha in csvreader:
        # Caso dado irrelevante para ordenação, não o armazena
        if linha[header] == "NA":
            pass
        else:
            # Valida para que não tenha dados negativos
            if not float(linha[header]) < 0:
                linhas.append(linha)

    arquivo.close()

    return linhas, header

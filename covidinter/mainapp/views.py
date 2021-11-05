from django.shortcuts import render
from django.views.generic import View
from django.contrib.staticfiles.storage import staticfiles_storage
import csv
from django.http import HttpResponse


# Create your views here.

class MainPage(View):
    # Limita quais campos podem ser buscado no formulario
    tipos_ordenacao = ['Novos Casos', 'Total de Casos', 'Novas Mortes', 'Total de Mortes']

    def post(self, request):
        context = {'tipos_ordenacao': self.tipos_ordenacao}
        for envio in request.POST:
            if envio == 'ordenar':
                lista, valor = realiza_ordenacao(request.POST['ordenar'])
                request.session['lista'] = lista
                request.session['valor'] = valor
            elif envio == 'buscar':
                dados_busca = realiza_busca(request.session['lista'], request.session['valor'],request.POST['buscar'])
                context = {'tipos_ordenacao': self.tipos_ordenacao,'dados_busca': dados_busca}
        return render(request, 'mainapp/page.html', context)

    def get(self, request):

        context = {'tipos_ordenacao': self.tipos_ordenacao}
        return render(request, 'mainapp/page.html', context)


# Utilizado busca liner devido a possibilidade de elementos repetidos
def realiza_busca(listas, index, busca):
    resultados = []
    for x in range(len(listas)):
        if float(listas[x][index]) == int(busca):
            resultados.append(listas[x])

    return resultados





# Ordenação por Merge Sort
# tipo = tipo da ordenação selecionada pelo usuário, Buscar por Mortes, Quantidades de casos ...
def realiza_ordenacao(tipo):
    linhas, index = extrair_dados_csv(tipo)

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

    # Teste em minimundo
    # linhasteste = [[1, 8], [2, 4], [3, 1], [4, 5], [5, 2], [6, 7], [7, 9], [8, 3], ]
    # linhas = mergesort(linhasteste,1)
    linhas = mergesort(linhas, index)

    return linhas, index


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

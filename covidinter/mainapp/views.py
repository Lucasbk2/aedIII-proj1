from django.shortcuts import render
from django.views.generic import View
from django.contrib.staticfiles.storage import staticfiles_storage
import csv
from django.http import HttpResponse
# Create your views here.

class MainPage(View):
    #Limita quais campos podem ser buscado no formulario
    tipos_ordenacao = ['Novos Casos','Total de Casos','Novas Mortes','Total de Mortes']
    def post(self,request):
        context = {'tipos_ordenacao': self.tipos_ordenacao}
        realiza_ordenacao(request.POST['select'])
        return render(request, 'mainapp/page.html', context)
    def get(self,request):
        context = {'tipos_ordenacao':self.tipos_ordenacao}
        return render(request,'mainapp/page.html',context)

def realiza_ordenacao(tipo):
    linhas,index = extrair_csv(tipo)
    return index

def extrair_csv(tipo):
    linhas = [] # Armazena as linhas do csv
    if tipo == 'Novos Casos':
        tipo = 'new_cases'
    elif tipo == 'Total de Casos':
        tipo = 'total_cases'
    elif tipo == 'Novas Mortes':
        tipo = 'new_deaths'
    elif tipo == 'Total de Mortes':
        tipo = 'total_deaths'

    #Leitura do arquivo
    path = staticfiles_storage.path('mainapp/InternationalCovid19Cases.csv')
    arquivo = open(path)
    csvreader = csv.reader(arquivo)

    header = next(csvreader).index(tipo) # Armazena o index da coluna que será utilizada

    for linha in csvreader:
        linhas.append(linha)

    arquivo.close()

    return linhas,header
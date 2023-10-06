from django.shortcuts import render, redirect # Importando funções do djando que estão em shortcuts
from perfil.models import Categoria, Conta # Importando Categoria e Conta da pasta PERFIL\MODELS
from django.http import HttpResponse, FileResponse # Impostanções do django que estão em http
from .models import Valores # Importando os valores de Models DESSA pasta
from django.contrib import messages # Importando as mensagens que definimos no core
from django.contrib.messages import constants # Importando as constantes que definimos no core
from datetime import datetime, timedelta # Biblioteca nativa do python para conversao de date
from django.template.loader import render_to_string # Carregaento do partial de extrato para html
import os # Concatenação de diretórios
from django.conf import settings  # Ter acesso ao base_dir
from weasyprint import HTML # Importando extensão
from io import BytesIO # Importando biblioteza do python, para salvar em memória ao invés de salvar em disco 

from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Conta, Categoria, Valores
from django.contrib import messages
from django.contrib.messages import constants

def novo_valor(request):
    if request.method == "GET":
        contas = Conta.objects.all()
        categorias = Categoria.objects.all() 
        return render(request, 'novo_valor.html', {'contas': contas, 'categorias': categorias})
    elif request.method == "POST":
        valor = request.POST.get('valor')
        categoria = request.POST.get('categoria')
        descricao = request.POST.get('descricao')
        data = request.POST.get('data')
        conta = request.POST.get('conta')
        tipo = request.POST.get('tipo')
        
        if not valor.strip() or not categoria or not data or not conta or not tipo:
            messages.add_message(request, constants.ERROR, 'Preencha todos os campos')
            return redirect('/extrato/novo_valor')
        
        try:
            valor = float(valor)
            if valor <= 0:
                messages.add_message(request, constants.WARNING, 'O valor deve ser maior que zero')
                return redirect('/extrato/novo_valor')
        except ValueError:
            messages.add_message(request, constants.WARNING, 'Valor inválido')
            return redirect('/extrato/novo_valor')
        
        conta_obj = Conta.objects.get(id=conta)
        if tipo == 'E':
            conta_obj.valor += valor
            messages.add_message(request, constants.INFO, 'Entrada cadastrada com sucesso')
        else:
            conta_obj.valor -= valor
            messages.add_message(request, constants.INFO, 'Saída cadastrada com sucesso')
        
        conta_obj.save()
        
        valor_obj = Valores(
            valor=valor,
            categoria_id=categoria,
            descricao=descricao,
            data=data,
            conta_id=conta,
            tipo=tipo,
        )
        valor_obj.save()
    
        return redirect('/extrato/novo_valor')

    

        #TODO: Mensagem processada de acordo com o tipo

def view_extrato(request):
    categorias = Categoria.objects.all()
    contas = Conta.objects.all()

    conta_get = request.GET.get('conta')
    categoria_get = request.GET.get('categoria')
    periodo_get = request.GET.get('periodo')

    valores = Valores.objects.all()

    if conta_get:
        conta_selecionada = Conta.objects.get(id=conta_get)
        valores = valores.filter(conta__id=conta_get)
    else:
        conta_selecionada = None

    if categoria_get:
        categoria_selecionada_no_filtro = Categoria.objects.get(id=categoria_get)
        valores = valores.filter(categoria__id=categoria_get)
    else:
        categoria_selecionada_no_filtro = None

    periodo_default = '7'  # Definir o valor padrão para o período

    if periodo_get:
        periodo_default = periodo_get
        # Calcular a data de início do período com base no valor do período_get
        data_inicio = datetime.now().date() - timedelta(days=int(periodo_get))
        # Filtrar os valores com base na data de início
        valores = valores.filter(data__gte=data_inicio)

    if 'limpar_filtros' in request.GET:
        return redirect('view_extrato')

    return render(request, 'view_extrato.html', {'valores': valores, 'contas': contas, 'categorias': categorias, 'periodo_default': periodo_default, 'categoria_selecionada_no_filtro': categoria_selecionada_no_filtro, 'conta_selecionada': conta_selecionada})

def exportar_pdf(request):
    valores = Valores.objects.filter(data__month=datetime.now().month)
    
    path_template = os.path.join(settings.BASE_DIR, 'templates/partials/extrato.html')
    template_render = render_to_string(path_template, {'valores': valores})
    
    path_output = BytesIO()

    HTML(string=template_render).write_pdf(path_output)

    path_output.seek(0)
    

    return FileResponse(path_output, filename="extrato.pdf")
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Conta
from .models import Categoria
from django.contrib import messages
from django.contrib.messages import constants
from .utils import calcula_total, calcula_equilibrio_financeiro
from extrato.models import Valores
from datetime import datetime 
# import re


def home(request):
    valores = Valores.objects.filter(data__month=datetime.now().month)
    entradas = valores.filter(tipo='E')
    saidas = valores.filter(tipo='S')

    total_entradas = calcula_total(entradas, 'valor')
    total_saidas = calcula_total(saidas, 'valor')


    contas = Conta.objects.all()    
    total_contas = calcula_total(contas, 'valor')
    saldo_total = calcula_total(contas, 'valor')

    percentual_gastos_essenciais, percentual_gastos_nao_essenciais = calcula_equilibrio_financeiro()
    return render(request, 'home.html', {'contas': contas,
                                         'total contas': total_contas ,
                                         'saldo_total': saldo_total,
                                         'total_entradas': total_entradas,
                                         'total_saidas': total_saidas,
                                         'percentual_gastos_essenciais': int(percentual_gastos_essenciais),
                                         'percentual_gastos_nao_essenciais': int(percentual_gastos_nao_essenciais)})


def gerenciar(request):
    contas = Conta.objects.all()
    bancos = Conta.banco_choices
    tipos = Conta.tipo_choices
    categorias = Categoria.objects.all()
    total_contas = calcula_total(contas, 'valor')
    return render(request, 'gerenciar.html', {'contas': contas, 'bancos': bancos, 'tipos': tipos, 'total_contas': total_contas, 'categorias': categorias})

def cadastrar_banco(request):
    apelido = request.POST.get('apelido')
    banco = request.POST.get('banco')
    tipo = request.POST.get('tipo')
    valor = request.POST.get('valor')
    icone = request.FILES.get('icone')

    # Validação do campo 'apelido'
    if len(apelido.strip()) == 0 or len(valor.strip()) == 0:
        messages.add_message(request, constants.ERROR, 'Preencha todos os campos')
        return redirect('/perfil/gerenciar/')

    if len(apelido) > 50:
        messages.add_message(request, constants.ERROR, 'O apelido deve ter no máximo 50 caracteres')
        return redirect('/perfil/gerenciar/')
    
     # Verificar se o nome da categoria contém apenas letras e espaços
    if not re.match(r'^[a-zA-Z\s]+$', apelido):
        messages.add_message(request, constants.ERROR, 'O campo apelido deve conter apenas letras e espaços')
        return redirect('/perfil/gerenciar/')
    
    # Validação do campo 'banco'
    bancos_validos = ['NU', 'BR',] 
    if banco not in bancos_validos:
        messages.add_message(request, constants.ERROR, 'Tipo de banco inválido')
        return redirect('/perfil/gerenciar/')
    
    # Validação do campo 'tipo'
    tipos_validos = ['pf', 'pj',] 
    if tipo not in tipos_validos:
        messages.add_message(request, constants.ERROR, 'Tipo de conta inválido')
        return redirect('/perfil/gerenciar/')
    
    # Validação do campo 'valor'
    try:
        valor = float(valor)
        if valor <= 0:
            messages.add_message(request, constants.ERROR, 'O valor deve ser maior que zero')
            return redirect('/perfil/gerenciar/')
    except ValueError:
        messages.add_message(request, constants.ERROR, 'Valor inválido')
        return redirect('/perfil/gerenciar/')
    
    conta = Conta(
        apelido=apelido,
        banco=banco,
        tipo=tipo,
        valor=valor,
        icone=icone
    )

    conta.save()
    messages.add_message(request, constants.SUCCESS, 'Conta cadastrada com sucesso')
    return redirect('/perfil/gerenciar')


def deletar_banco(request, id):
    conta = Conta.objects.get(id=id)
    conta.delete()

    messages.add_message(request, constants.SUCCESS, 'Conta deletada com sucesso')
    return redirect('/perfil/gerenciar')

def cadastrar_categoria(request):
    nome = request.POST.get('categoria')
    essencial = bool(request.POST.get('essencial'))

     # Validação do campo 'categoria'
    if not isinstance(nome, str) or nome.strip() == "":
        messages.add_message(request, constants.ERROR, 'O campo categoria é inválido')
        return redirect('/perfil/gerenciar/')
    
     # Validação do número máximo de caracteres (50)
    if len(nome) > 50:
        messages.add_message(request, constants.ERROR, 'O campo categoria deve ter no máximo 50 caracteres')
        return redirect('/perfil/gerenciar/')

    # Verificar se a categoria já existe
    if Categoria.objects.filter(categoria=nome).exists():
        messages.add_message(request, constants.ERROR, 'A categoria já existe')
        return redirect('/perfil/gerenciar/')
     
    # Verificar se o nome da categoria contém apenas letras e espaços
    if not re.match(r'^[a-zA-Z\s]+$', nome):
        messages.add_message(request, constants.ERROR, 'O campo categoria deve conter apenas letras e espaços')
        return redirect('/perfil/gerenciar/')

    categoria = Categoria(
        categoria=nome,
        essencial=essencial
    )

    categoria.save()

    messages.add_message(request, constants.SUCCESS, 'Categoria cadastrada com sucesso')
    return redirect('/perfil/gerenciar/')


def update_categoria(request, id):
    categoria = Categoria.objects.get(id=id)
    categoria.essencial = not categoria.essencial
    categoria.save()
    return redirect('/perfil/gerenciar/')

def dashboard(request):
    dados = {}
    categorias = Categoria.objects.all()

    for categoria in categorias:
        total = 0
        valores = Valores.objects.filter(categoria=categoria)
        for v in valores:
            total += v.valor

        dados[categoria.categoria] = total

    return render(request, 'dashboard.html', {'labels': list(dados.keys()), 
                                              'values': list(dados.values())})
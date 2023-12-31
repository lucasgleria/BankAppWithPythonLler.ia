from django.shortcuts import render, redirect
from perfil.models import Categoria
from .models import ContaPagar, ContaPaga
from django.contrib import messages
from django.contrib.messages import constants
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse

def definir_contas(request):
    if request.method == "GET":
        categorias = Categoria.objects.all()
        return render(request, 'definir_contas.html', {'categorias': categorias})
    else:
        titulo = request.POST.get('titulo')
        categoria = request.POST.get('categoria')
        descricao = request.POST.get('descricao')
        valor = request.POST.get('valor')
        dia_pagamento = request.POST.get('dia_pagamento')

        conta = ContaPagar(
            titulo=titulo,
            categoria_id=categoria,
            descricao=descricao,
            valor=valor,
            dia_pagamento=dia_pagamento
        )

        conta.save()

        messages.add_message(request, constants.SUCCESS, 'Conta cadastrada com sucesso')
        return redirect('/contas/definir_contas')

def ver_contas(request):
    MES_ATUAL = datetime.now().month
    DIA_ATUAL = datetime.now().day
    
    contas = ContaPagar.objects.all()

    contas_pagas = ContaPaga.objects.filter(data_pagamento__month=MES_ATUAL).values('conta')

    contas_vencidas = contas.filter(dia_pagamento__lt=DIA_ATUAL).exclude(id__in=contas_pagas)
    total_contas_vencidas = contas_vencidas.count()
    
    contas_proximas_vencimento = contas.filter(dia_pagamento__lte=DIA_ATUAL + 5).filter(dia_pagamento__gte=DIA_ATUAL).exclude(id__in=contas_pagas)
    total_contas_proximas_vencimento = contas_proximas_vencimento.count()
    
    restantes = contas.exclude(id__in=contas_vencidas).exclude(id__in=contas_pagas).exclude(id__in=contas_proximas_vencimento)
    total_restantes = restantes.count()

    return render(request, 'ver_contas.html', {'contas_vencidas': contas_vencidas, 
                                               'contas_proximas_vencimento': contas_proximas_vencimento, 
                                               'restantes': restantes,
                                               'contas_vencidas_count': contas_vencidas.count(), 
                                               'contas_proximas_vencimento_count': contas_proximas_vencimento.count(), 
                                               'restantes_count': restantes.count(),
                                               'contas_pagas_count': contas_pagas.count()
                                               })
    

@csrf_exempt
def pagar(request, id):
    paga = json.load(request)['paga']
    contas_pagas = ContaPaga.objects.get(id=id)
    contas_pagas.conta = paga 
    contas_pagas.save()
    contas_pagas.delete()

    return JsonResponse({'status': 'Sucesso'})

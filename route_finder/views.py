from django.shortcuts import render
from django.http import JsonResponse
# from invoice_reader.core.entities.preinvoice_df import PreInvoice
# Create your views here.


def route_finder(request):
    # invoice = PreInvoice()
    return JsonResponse({'teste': 'teste'})

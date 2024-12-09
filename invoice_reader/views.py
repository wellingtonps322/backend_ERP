import sched
import time

from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from invoice_reader.core.entities.preinvoice_df import PreInvoice
# Create your views here.

running_task = False

schedule = sched.scheduler(time.time, time.sleep)


def set_insert_invoice(file):
    global running_task

    invoice = PreInvoice()
    response = invoice.getPreInvoice_df(file=file)

    running_task = False

    response_keys = list(response.keys())
    if not 'error' in response_keys and not 'duplicity' in response_keys:
        return JsonResponse({'message': 'Invoice was inserted successfully'}, status=200)
    elif 'duplicity' in response_keys:
        return JsonResponse(response, status=403)
    else:
        return JsonResponse({'error': 'Error to insert the invoice'}, status=400)


@csrf_exempt
def insert_invoice(request):
    global running_task

    if request.method == 'POST':
        if not running_task:
            try:
                running_task = True
                invoice_file = request.FILES['file']
                print('Received data:', invoice_file)

                # Aqui você pode realizar as operações desejadas com o arquivo, como salvar no banco de dados.
                # Por exemplo, se 'PreInvoice' for um modelo que você definiu, você pode fazer algo como:
                response = set_insert_invoice(file=invoice_file)
                print(f'{settings.BASE_DIR}' + r'\media\invoices\invoice.csv')

                return response
            except Exception as e:
                print(e)
                running_task = False
                return JsonResponse(response, status=403)

    return JsonResponse({'error': 'There is already an invoice being entered'}, status=503)

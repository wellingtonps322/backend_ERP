import time
import json

from django.shortcuts import render
from django.http import JsonResponse, FileResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from payment_voucher_creator.core.payment_voucher import PaymentVoucher

# Create your views here.


@csrf_exempt
def payment_voucher(request) -> JsonResponse:
    """
        Essa método view recebe uma request cos os dados de rota do colaborador para gerar o seu comprovante de pagamento
    """
    if request.method == "POST":
        payment_mirror_data = json.loads(request.body)

        print('Receveid data:', payment_mirror_data)

        if payment_mirror_data:
            def file_name_creator(payment_data: dict) -> str:
                name = payment_data['employeeInformation']['name'].replace(
                    " ", "_")
                date = payment_data['createdAt'].replace("/", "-")
                user_name = payment_data['userName'].upper().replace(" ", "_")

                return f'{name}&{date}&{user_name}'

            file_name = file_name_creator(payment_mirror_data)
            payment_voucher_path = PaymentVoucher().create_payment_voucher(
                file_name, payment_mirror_data)
            if payment_voucher_path:
                with open(payment_voucher_path, 'rb') as file:
                    response = HttpResponse(
                        file.read(), content_type='application/pdf')
                    response['Content-Disposition'] = f'attachment; filename="{
                        file_name}.pdf"'
                    return response
    return JsonResponse({'error': 'Method not allowed'}, status=405)

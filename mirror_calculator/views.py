import datetime
import math
import time

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from mirror_calculator.core.database.recorder import Recorder
from mirror_calculator.core.database.reader import Reader
from mirror_calculator.core.entities.payment_calculator import PaymentCalculator

# Create your views here.
running_task = False


@csrf_exempt
def mirror_calculate(request) -> JsonResponse:
    '''
        Essa método view recebe uma request com o período da fatura:
        POST - solicita o cálculo dos espelhos da fatura solicitada pelo período especificado na requisição.
    '''

    def isInvoiceOld(period):
        periods = Reader().getAllPeriodsFromInvoiceInformation()

        def period_code_reader(period: str) -> dict[int]:
            year = int(period[:4]) if period[:4].isnumeric(
            ) else print('error')
            month = int(period[4:6]) if period[4:6].isnumeric(
            ) else print('error')
            fortnight = int(period[-1])
            return {
                'year': year,
                'month': month,
                'fortnight': fortnight
            }

        def period_code_creator(period_formatted: dict[int]) -> str:
            year = f"{period_formatted["year"]}"
            month = f"{period_formatted["month"]}" if period_formatted["month"] >= 10 else f"0{
                period_formatted["month"]}"
            fortnight = f"Q{period_formatted["fortnight"]}"

            period_code = f"{year}{month}{fortnight}"

            return period_code

        def period_comparator(first_period: dict[int], second_period: dict[int]) -> dict[int]:
            """Return recent period"""

            first_period = period_code_reader(first_period)
            second_period = period_code_reader(second_period)

            if first_period["year"] != second_period["year"]:
                return max(first_period, second_period, key=lambda x: x["year"])
            elif first_period["month"] != second_period["month"]:
                return max(first_period, second_period, key=lambda x: x["month"])
            elif first_period["fortnight"] != second_period["fortnight"]:
                return max(first_period, second_period, key=lambda x: x["fortnight"])
            else:
                return first_period

        for other_period in periods:

            # Verifica se o período da fatura requisitado para cálculo é recente referente ao do looping
            result = period_code_creator(
                period_comparator(period, other_period[0]))

            if result == period:
                continue
            else:
                return True
        return False

    if request.method == 'POST':
        global running_task

        if not running_task:
            try:
                period = request.GET['period']
                print('Received data:', period)

                if not isInvoiceOld(period):

                    paymentCalculator = PaymentCalculator(period)
                    initial_time = time.time()
                    payment_data = paymentCalculator.getPaymentMirror()

                    recorder = Recorder()

                    response = recorder.insertPaymentData(payment_data)

                    end_time = time.time()
                    total_time = end_time - initial_time

                    print(f'The time to execute was: {total_time}')
                    running_task = False
                    if response:
                        return JsonResponse({'completed': 'Invoice was calculated successfully'})
                    else:
                        return JsonResponse({'error': 'Error to calculate mirrors'}, status=400)
                else:
                    return JsonResponse({'error': 'Invoice is old'}, status=401)

            except Exception as e:
                print(e)
                running_task = False
                return JsonResponse({'warning': 'An invoice is already in the calculation process '}, status=403)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

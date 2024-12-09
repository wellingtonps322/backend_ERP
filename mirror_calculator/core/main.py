import sys
import time

from mirror_calculator.core.database.recorder import Recorder

from mirror_calculator.core.entities.payment_calculator import PaymentCalculator

if len(sys.argv) > 1:
    period = sys.argv[1]

else:
    period = '202312Q1'

paymentCalculator = PaymentCalculator(period)

initial_time = time.time()

payment_data = paymentCalculator.getPaymentMirror()

recorder = Recorder()
recorder.insertPaymentData(payment_data)
end_time = time.time()

total_time = end_time - initial_time

print(f'The time to execute was: {total_time}')

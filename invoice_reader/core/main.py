from entities.preinvoice_df import PreInvoice
from django.conf import settings
import sys


preinvoice = PreInvoice()

preinvoice.getPreInvoice_df(file='teste')

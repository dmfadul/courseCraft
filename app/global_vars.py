import math
from datetime import datetime, timedelta
from .global_config import *


STARTING_DATE = datetime.strptime(START_DATE_STRING, "%d/%m/%Y").date()
ENDING_DATE = datetime.strptime(END_DATE_STRING, "%d/%m/%Y").date()
DURATION = ENDING_DATE - STARTING_DATE
NUM_WEEKS = math.ceil(DURATION.days / 7)

NUMBER_OF_INTERVALS = len(INTERVALS_SLOTS)

HOLIDAYS = [datetime.strptime(f"{holiday}/{SCHOOL_YEAR}", "%d/%m/%Y").date() for holiday in holidays_dates]

DIAS_DA_SEMANA = ["SEGUNDA-FEIRA", "TERÇA-FEIRA", "QUARTA-FEIRA", "QUINTA-FEIRA", "SEXTA-FEIRA", "SÁBADO"]

months_translation = {
    "January": "Janeiro",
    "February": "Fevereiro",
    "March": "Março",
    "April": "Abril",
    "May": "Maio",
    "June": "Junho",
    "July": "Julho",
    "August": "Agosto",
    "September": "Setembro",
    "October": "Outubro",
    "November": "Novembro",
    "December": "Dezembro"
}

chronological = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

MESES = list(months_translation.values())
MESES_ABR = [month[:3] for month in MESES]
MONTHS = list(set([date.strftime("%B") for date in [STARTING_DATE + timedelta(weeks=i) for i in range(NUM_WEEKS+1)]]))
MONTHS = [chronological.index(month) + 1 for month in chronological if month in MONTHS]

import pandas as pd
from django.core.management.base import BaseCommand
from myapp.models import Company, Specialty, Vacancy

from .data import companies, jobs, specialties

# Добавить в модель метод clean() на проверку что макс зарплата больше мин зарплаты в вилке

MAPPING_MODEL_ELEMENTS = {
    Company: companies,
    Vacancy: jobs,
    Specialty: specialties,
}

MAIN_TYPES = {
    'id': int, 'employee_count': int,
    'company': int, 'salary_from': float,
    'salary_to': float
}

MAPPING_FIELDS = {
    Vacancy: {
        'salary_from': 'salary_min',
        'salary_to': 'salary_max',
        'posted': 'published_at'
    },
    Company: {
        'title': 'name'
    },
}


def change_types(element_for_load, model, types=MAIN_TYPES):
    df = pd.DataFrame(element_for_load)
    if 'id' not in df:
        df['id'] = df.index + 1
    df = df.astype({k: v for k, v in types.items() if k in df.columns})
    return df.rename(columns=MAPPING_FIELDS.get(model)).to_dict('records')


class Command(BaseCommand):
    def handle(self, *args, **options):
        for model, loads_elements in MAPPING_MODEL_ELEMENTS.items():
            for one_row in change_types(loads_elements, model):
                new_record = model(**one_row)
                new_record.save()
                # нужны связи для ключей между моделями, погуглить как

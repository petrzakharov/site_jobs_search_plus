import pandas as pd
from django.core.management.base import BaseCommand
from myapp.models import Company, Specialty, Vacancy

from .data import companies, jobs, specialties

MAPPING_MODEL_ELEMENTS = {
    Company: companies,
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
    Specialty: {
        '': ''
    }
}


def change_types(element_for_load, model, types=MAIN_TYPES):
    """
    Ренейминг и изменение типов в предоставляемых данных
    """
    df = pd.DataFrame(element_for_load)
    if 'id' not in df:
        df['id'] = df.index + 1
    df = df.astype({k: v for k, v in types.items() if k in df.columns})
    return df.rename(columns=MAPPING_FIELDS.get(model)).to_dict('records')


class Command(BaseCommand):
    """
    Загрузка данных в модели
    """
    def handle(self, *args, **options):
        for model, loads_elements in MAPPING_MODEL_ELEMENTS.items():
            for row in change_types(loads_elements, model):
                new_record = model(**row)
                new_record.save()

        for row in change_types(jobs, Vacancy):
            row['company'] = Company.objects.get(id=row['company'])
            row['specialty'] = Specialty.objects.get(code=row['specialty'])
            new_record_vacancy = Vacancy(**row)
            new_record_vacancy.clean()
            new_record_vacancy.save()

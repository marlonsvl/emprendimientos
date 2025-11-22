from django.core.management.base import BaseCommand, CommandError
from gastronomia.models import Establecimiento
from django.utils import timezone
import pandas as pd




class Command(BaseCommand):
    help = 'Load data from Excel file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', nargs='+',type=str)
        #parser.add_argument('sheet_name', nargs='+', type=str)
    
    def to_float_safe(val):
        if pd.isna(val):
            return None
        return float(str(val).replace('−','-'))


    def handle(self, *args, **options):
        """
        This command helps to load data from Excel file using this command:
        python manage.py loadingestablecimientos /Users/santiagovinan/Downloads/data_empr.xlsx survey
        """
        start_time = timezone.now()
        print(start_time)
        print(options['file_path'][0])
        #print(options['sheet_name'][0])
        #data = pd.read_excel('/Users/santiagovinan/Downloads/data_empr.xlsx', sheet_name='survey')
        #data = pd.read_excel(options['file_path'][0], 
        #    sheet_name=options['sheet_name'][0])
        data = pd.read_csv(options['file_path'][0])
        #data['18. Indique el número de mesas que posee el emprendimiento'] = data['18. Indique el número de mesas que posee el emprendimiento'].fillna(0)
        #data['19. plazas'] = data['19. plazas'].fillna(0)
        #data['24. Precio promedio'] = data['24. Precio promedio'].fillna(0.00)
        print(data[['longitude','latitude']].head())
        print(data[['longitude','latitude']].dtypes)
        data['longitude'] = (
            data['longitude']
            .astype(str)
            .str.replace('−', '-', regex=False)   # sustituir el signo raro
            .astype(float)
        )

        data['latitude'] = (
            data['latitude']
            .astype(str)
            .str.replace('−', '-', regex=False)
            .astype(float)
        )

        estabs = [
            Establecimiento(
                 nombre = row[0],
                 parroquia = row[1],
                 sector = row[2],
                 #fecha = row[6],
                 telefono = row[3],
                 email = row[4],
                 propietario = row[5],
                 tipo_turismo = row[6],
                 experiencia = row[7],
                 asociacion = row[8],
                 ruc = row[9],
                 estado_local = row[10],
                 servicios_produccion = row[11],
                 licencia_gad_loja = row[12],
                 arcsa = row[13],
                 turismo = row[14],
                 equipos = row[15],
                 pagina_web = row[16],
                 facebook = row[17],
                 instagram = row[18],
                 tiktok = row[19],
                 whatsapp = row[2],
                 tipo = row[21],
                 mesas = row[22],
                 plazas = row[23],
                 banio = row[24],
                 complementarios = row[25],
                 oferta = row[26],
                 menu = row[27],
                 tipo_servicio = row[28],
                 precio_promedio = row[29],
                 procesos = row[30],
                 materia_prima = row[31],
                 proveedores = row[32],
                 numero_proveedores = row[33],
                 #tipo_materia_prima = row[33],
                 numero_mujeres = row[34],
                 numero_hombres = row[35],
                 tiempo_trabajando = row[36],
                 personal_capacitado = row[37],
                 frecuencia_capacitacion = row[38],
                 dependencia_ingresos = row[39],
                 genero = row[40],
                 nivel_educacion = row[41],
                 edad = row[42],
                 estado_civil = row[43],
                 longitude = row[44],
                 latitude = row[45],
                 horario = row[46],
                 categoria = row[47]
            )
            for i, row in data.iterrows()     
        ]
        Establecimiento.objects.bulk_create(estabs)
        end_time = timezone.now()
        self.stdout.write(
            self.style.SUCCESS(
                f"Loading xlsx file took: {(end_time-start_time).total_seconds()} seconds."
            )
        )
        

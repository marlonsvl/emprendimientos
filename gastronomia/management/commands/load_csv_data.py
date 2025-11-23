import csv
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from gastronomia.models import Establecimiento  


class Command(BaseCommand):
    help = 'Load Establecimiento data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to the CSV file to import'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before importing'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=500,
            help='Batch size for bulk create (default: 500)'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        batch_size = options['batch_size']
        
        if options['clear']:
            Establecimiento.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared existing data'))

        try:
            with open(csv_file, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                
                # Debug: Print actual column names
                self.stdout.write(self.style.WARNING(f'CSV columns: {reader.fieldnames}'))
                
                created_count = 0
                error_count = 0
                batch = []
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Clean whitespace from row keys
                        row = {k.strip(): v for k, v in row.items()}
                        
                        # Convert empty strings to appropriate defaults
                        data = self._clean_row(row)
                        
                        # Create the Establecimiento instance
                        establecimiento = Establecimiento(**data)
                        batch.append(establecimiento)
                        
                        # Bulk create when batch reaches batch_size
                        if len(batch) >= batch_size:
                            Establecimiento.objects.bulk_create(batch, ignore_conflicts=False)
                            created_count += len(batch)
                            self.stdout.write(f'Created {created_count} records so far...')
                            batch = []
                            
                            # Clear database connections to prevent memory issues
                            connection.close()
                        
                    except (ValidationError, ValueError, KeyError) as e:
                        error_count += 1
                        self.stdout.write(
                            self.style.ERROR(f'Error in row {row_num}: {str(e)}')
                        )
                        self.stdout.write(
                            self.style.ERROR(f'Row data: {row}')
                        )
                        continue
                
                # Create remaining records in batch
                if batch:
                    Establecimiento.objects.bulk_create(batch, ignore_conflicts=False)
                    created_count += len(batch)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n✓ Successfully imported {created_count} records'
                    )
                )
                if error_count > 0:
                    self.stdout.write(
                        self.style.WARNING(f'{error_count} rows had errors')
                    )
                    
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'File not found: {csv_file}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Unexpected error: {str(e)}')
            )

    def _clean_row(self, row):
        """Convert CSV row data to appropriate types"""
        
        def to_int(value):
            if value is None:
                return 0
            value_str = str(value).strip()
            if not value_str:
                return 0
            try:
                return int(float(value_str))
            except (ValueError, TypeError):
                return 0
        
        def to_decimal(value):
            if value is None:
                return Decimal('0.00')
            value_str = str(value).strip()
            if not value_str:
                return Decimal('0.00')
            try:
                return Decimal(value_str)
            except:
                return Decimal('0.00')
        
        def to_string(value):
            if value is None:
                return ''
            return str(value).strip()
        
        # Debug: Show what value we're getting for nombre
        nombre_value = row.get('nombre')
        if nombre_value is None or not str(nombre_value).strip():
            self.stdout.write(
                self.style.WARNING(f'WARNING: nombre is empty. Available keys: {list(row.keys())}')
            )
        
        cleaned = {
            'nombre': to_string(row.get('nombre')),
            'parroquia': to_string(row.get('parroquia')),
            'sector': to_string(row.get('sector')),
            'telefono': to_string(row.get('telefono')),
            'email': to_string(row.get('email')) or 'noemail@example.com',
            'propietario': to_string(row.get('propietario')),
            'tipo_turismo': to_string(row.get('tipo_turismo')) or 'No especificado',
            'experiencia': to_int(row.get('experiencia')),
            'asociacion': to_string(row.get('asociacion')) or 'No',
            'ruc': to_string(row.get('ruc')) or 'No',
            'estado_local': to_string(row.get('estado_local')) or 'Propio',
            'servicios_produccion': to_string(row.get('servicios_produccion')),
            'licencia_gad_loja': to_string(row.get('licencia_gad_loja')) or 'No',
            'arcsa': to_string(row.get('arcsa')) or 'No',
            'turismo': to_string(row.get('turismo')) or 'No',
            'equipos': to_string(row.get('equipos')),
            'pagina_web': to_string(row.get('pagina_web')) or 'No',
            'facebook': to_string(row.get('facebook')) or 'No',
            'instagram': to_string(row.get('instagram')) or 'No',
            'tiktok': to_string(row.get('tiktok')) or 'No',
            'whatsapp': to_string(row.get('whatsapp')) or 'No',
            'tipo': to_string(row.get('tipo')),
            'mesas': to_int(row.get('mesas')),
            'plazas': to_int(row.get('plazas')),
            'banio': to_string(row.get('banio')) or 'No',
            'complementarios': to_string(row.get('complementarios')),
            'oferta': to_string(row.get('oferta')),
            'menu': to_string(row.get('menu')),
            'tipo_servicio': to_string(row.get('tipo_servicio')),
            'precio_promedio': to_decimal(row.get('precio_promedio')),
            'procesos': to_string(row.get('procesos')),
            'materia_prima': to_string(row.get('materia_prima')),
            'proveedores': to_string(row.get('proveedores')),
            'numero_proveedores': to_int(row.get('numero_proveedores')),
            'numero_mujeres': to_int(row.get('numero_mujeres')),
            'numero_hombres': to_int(row.get('numero_hombres')),
            'tiempo_trabajando': to_int(row.get('tiempo_trabajando')),
            'personal_capacitado': to_string(row.get('personal_capacitado')) or 'No',
            'frecuencia_capacitacion': to_string(row.get('frecuencia_capacitacion')),
            'dependencia_ingresos': to_string(row.get('dependencia_ingresos')),
            'genero': to_string(row.get('genero')) or 'Otro',
            'nivel_educacion': to_string(row.get('nivel_educacion')) or 'No especificado',
            'edad': to_int(row.get('edad')),
            'estado_civil': to_string(row.get('estado_civil')),
            'longitude': to_decimal(row.get('longitude')),
            'latitude': to_decimal(row.get('latitude')),
            'horario': to_string(row.get('horario')),
            'categoria': to_string(row.get('categoria')),
            'photo_url': to_string(row.get('photo_url')) or 'https://picsum.photos/300/30',
            'video_url': to_string(row.get('video_url')),
            'gallery_urls': self._parse_urls(row.get('gallery_urls')),
        }
        
        return cleaned

    def _parse_urls(self, urls_string):
        """Parse comma-separated URLs into a list"""
        if urls_string is None:
            return []
        urls_str = str(urls_string).strip()
        if not urls_str:
            return []
        return [url.strip() for url in urls_str.split(',') if url.strip()]
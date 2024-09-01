# comandos para poblar la base de datos con datos simulados
from django.core.management.base import BaseCommand
from jardines.models import Jardin
from niños.models import Niño, Asistencia
from usuarios.models import Usuario
from django.contrib.auth.models import Group
from faker import Faker
from datetime import timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Poblar la base de datos con datos simulados'

    def handle(self, *args, **kwargs):
        self.stdout.write(
            self.style.SUCCESS('Iniciando población de la base de datos con datos simulados'))

        # limpiar la base de datos
        self.stdout.write(self.style.WARNING('Limpiando la base de datos...'))
        Asistencia.objects.all().delete()
        Niño.objects.all().delete()
        Jardin.objects.all().delete()
        Usuario.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Base de datos limpiada exitosamente'))

        # Configurar Faker para usar nombres y direcciones en español
        fake = Faker('es_CO')

        self.stdout.write(self.style.WARNING('Creando usuario administrador...'))
        # Crear 1 usuario con el rol administrador
        user = Usuario.objects.create_user(
            username='admin',
            password='admin',
            first_name='admin',
            last_name='admin',
            email='admin@gmail.com'
        )
        user.groups.add(Group.objects.get(name='Administrador'))
        self.stdout.write(self.style.SUCCESS('Usuario administrador creado exitosamente'))

        self.stdout.write(self.style.WARNING('Creando usuarios madre comunitaria...'))
        # Crear 5 usuarios con el rol madre comunitaria
        for i in range(5):
            first_name = fake.first_name_female()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}@example.com"
            username = f"{first_name.lower()}.{last_name.lower()}"
            user = Usuario.objects.create_user(
                username=username,
                password='Prueba1234',
                first_name=first_name,
                last_name=last_name,
                email=email
            )
            user.groups.add(Group.objects.get(name='Madre Comunitaria'))
            user.save()
        self.stdout.write(self.style.SUCCESS('Usuarios madre comunitaria creados exitosamente'))

        self.stdout.write(self.style.WARNING('Creando usuarios acudiente...'))
        # Crear 50 usuarios con el rol acudiente
        for i in range(50):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}@example.com"
            username = f"{first_name.lower()}.{last_name.lower()}"
            user = Usuario.objects.create_user(
                username=username,
                password='Prueba1234',
                first_name=first_name,
                last_name=last_name,
                email=email
            )
            user.groups.add(Group.objects.get(name='Acudiente'))
            user.save()
        self.stdout.write(self.style.SUCCESS('Usuarios acudiente creados exitosamente'))

        self.stdout.write(self.style.WARNING('Creando jardines...'))
        # Crear 5 jardines
        estados = ['Aprobado', 'En trámite', 'Negado']
        for i in range(5):
            Jardin.objects.create(
                nombre=fake.company(),
                direccion=fake.address(),
                estado=estados[i % 3]
            )
        self.stdout.write(self.style.SUCCESS('Jardines creados exitosamente'))

        self.stdout.write(self.style.WARNING('Creando niños...'))
        # Crear 100 niños
        eps = ['Sura', 'Colpatria', 'Sanitas', 'Nueva EPS', 'Famisanar', 'Cruz Blanca', 'Salud Total', 'Compensar', 'Axa', 'Liberty']
        for i in range(100):
            jardin = Jardin.objects.order_by('?').first()
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}@example.com"
            username = f"{first_name.lower()}.{last_name.lower()}"
            acudiente = Usuario.objects.filter(
                groups__name='Acudiente').order_by('?').first()
            Niño.objects.create(
                registro=fake.uuid4(),
                nombre=first_name,
                fecha_nacimiento=fake.date_of_birth(
                    minimum_age=1, maximum_age=5),
                tipo_sangre=fake.random_element(
                    elements=('O+', 'A+', 'B+', 'AB+')),
                ciudad_nacimiento=fake.city(),
                acudiente=acudiente,
                telefono=fake.phone_number(),
                direccion=fake.address(),
                eps=fake.random_element(elements=eps),
                jardin=jardin
            )
        self.stdout.write(self.style.SUCCESS('Niños creados exitosamente'))

        self.stdout.write(self.style.WARNING('Creando asistencias...'))
        # Crear asistencias para la ultima semana de lunes a viernes
        estados_asistencia = ['Sano', 'Decaído', 'Enfermo']
        for niño in Niño.objects.all():
            fecha = timezone.now()
            for i in range(7):
                if fecha.weekday() < 6:
                    Asistencia.objects.create(
                        niño=niño,
                        fecha=fecha,
                        estado_nino=fake.random_element(elements=estados_asistencia),
                    )
                fecha -= timedelta(days=1)

        self.stdout.write(self.style.SUCCESS('Asistencias creadas exitosamente'))

        self.stdout.write(self.style.SUCCESS('Población de la base de datos completada exitosamente'))

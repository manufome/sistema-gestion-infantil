# comandos para poblar la base de datos con datos simulados
from django.core.management.base import BaseCommand
from institutions.models import Institution
from students.models import Student, Attendance
from users.models import User
from django.contrib.auth.models import Group
from faker import Faker
from datetime import timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write(
            self.style.SUCCESS('Starting database population with sample data'))

        # Clear database
        self.stdout.write(self.style.WARNING('Clearing database...'))
        Attendance.objects.all().delete()
        Student.objects.all().delete()
        Institution.objects.all().delete()
        User.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Database cleared successfully'))

        # Configure Faker for Spanish names and addresses
        fake = Faker('es_CO')

        self.stdout.write(self.style.WARNING('Creating administrator user...'))
        # Create 1 admin user
        user = User.objects.create_user(
            username='admin',
            password='admin',
            first_name='admin',
            last_name='admin',
            email='admin@gmail.com'
        )
        user.groups.add(Group.objects.get(name='Administrator'))
        self.stdout.write(self.style.SUCCESS('Administrator user created successfully'))

        self.stdout.write(self.style.WARNING('Creating teacher users...'))
        # Create 5 teacher users
        for i in range(5):
            first_name = fake.first_name_female()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}@example.com"
            username = f"{first_name.lower()}.{last_name.lower()}"
            user = User.objects.create_user(
                username=username,
                password='Prueba1234',
                first_name=first_name,
                last_name=last_name,
                email=email
            )
            user.groups.add(Group.objects.get(name='Teacher'))
            user.save()
        self.stdout.write(self.style.SUCCESS('Teacher users created successfully'))

        self.stdout.write(self.style.WARNING('Creating guardian users...'))
        # Create 50 guardian users
        for i in range(50):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}@example.com"
            username = f"{first_name.lower()}.{last_name.lower()}"
            user = User.objects.create_user(
                username=username,
                password='Prueba1234',
                first_name=first_name,
                last_name=last_name,
                email=email
            )
            user.groups.add(Group.objects.get(name='Guardian'))
            user.save()
        self.stdout.write(self.style.SUCCESS('Guardian users created successfully'))

        self.stdout.write(self.style.WARNING('Creating institutions...'))
        # Create 5 institutions
        estados = ['Aprobado', 'En trámite', 'Negado']
        for i in range(5):
            Institution.objects.create(
                nombre=fake.company(),
                direccion=fake.address(),
                estado=estados[i % 3]
            )
        self.stdout.write(self.style.SUCCESS('Institutions created successfully'))

        self.stdout.write(self.style.WARNING('Creating students...'))
        # Create 100 students
        eps = ['Sura', 'Colpatria', 'Sanitas', 'Nueva EPS', 'Famisanar', 'Cruz Blanca', 'Salud Total', 'Compensar', 'Axa', 'Liberty']
        for i in range(100):
            institution = Institution.objects.order_by('?').first()
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}@example.com"
            username = f"{first_name.lower()}.{last_name.lower()}"
            guardian = User.objects.filter(
                groups__name='Guardian').order_by('?').first()
            Student.objects.create(
                registro=fake.uuid4(),
                nombre=first_name,
                fecha_nacimiento=fake.date_of_birth(
                    minimum_age=1, maximum_age=5),
                tipo_sangre=fake.random_element(
                    elements=('O+', 'A+', 'B+', 'AB+')),
                ciudad_nacimiento=fake.city(),
                guardian=guardian,
                telefono=fake.phone_number(),
                direccion=fake.address(),
                eps=fake.random_element(elements=eps),
                institution=institution
            )
        self.stdout.write(self.style.SUCCESS('Students created successfully'))

        self.stdout.write(self.style.WARNING('Creating attendance records...'))
        # Create attendance for the last week Monday to Friday
        estados_asistencia = ['Sano', 'Decaído', 'Enfermo']
        for student in Student.objects.all():
            fecha = timezone.now()
            for i in range(7):
                if fecha.weekday() < 6:
                    Attendance.objects.create(
                        student=student,
                        fecha=fecha,
                        estado_nino=fake.random_element(elements=estados_asistencia),
                    )
                fecha -= timedelta(days=1)

        self.stdout.write(self.style.SUCCESS('Attendance records created successfully'))

        self.stdout.write(self.style.SUCCESS('Database population completed successfully'))

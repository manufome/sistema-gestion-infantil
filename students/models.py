from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from users.models import User
from institutions.models import Institution



class Student(models.Model):
    registro = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=150)
    fecha_nacimiento = models.DateField()
    tipo_sangre = models.CharField(max_length=3)
    ciudad_nacimiento = models.CharField(max_length=100)
    guardian = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='students')
    telefono = models.CharField(max_length=15)
    direccion = models.TextField()
    eps = models.CharField(max_length=100)
    institution = models.ForeignKey(
        Institution, on_delete=models.CASCADE, related_name='students')
    fecha_registro = models.DateField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.nombre

    def clean(self):
        # Removed age restriction - now configurable per institution
        pass

    def get_edad(self):
        return (timezone.now().date() - self.fecha_nacimiento).days // 365


class Attendance(models.Model):
    fecha = models.DateField()
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name='attendances')
    estado_nino = models.CharField(max_length=20, choices=[
        ('Enfermo', 'Enfermo'),
        ('Sano', 'Sano'),
        ('Decaído', 'Decaído')
    ])

    def __str__(self):
        return f"{self.fecha} - {self.student.nombre} - {self.student.institution}"

    def clean(self):
        # Validación para asegurarse que el registro de asistencia sea entre 8 y 10 AM
        now = timezone.now()
        if not (now.hour >= 8 and now.hour <= 10):
            raise ValidationError(
                "El llamado de lista debe registrarse entre las 8 y las 10 de la mañana.")

        if self.estado_nino == 'Enfermo':
            # Lógica para reportar al administrador si el niño está enfermo
            pass


class AcademicProgress(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name='academic_progress')
    ano_escolar = models.IntegerField()
    nivel = models.CharField(max_length=20, choices=[
        ('Natal', 'Natal'),
        ('Prenatal', 'Prenatal'),
        ('Párvulo', 'Párvulo'),
        ('Jardín', 'Jardín'),
        ('Pre-jardín', 'Pre-jardín')
    ])
    notas = models.CharField(max_length=1, choices=[
        ('S', 'Superior'),
        ('A', 'Alto'),
        ('B', 'Bajo')
    ])
    descripcion = models.TextField()
    fecha_entrega = models.DateField()

    def __str__(self):
        return f"{self.student.nombre} - {self.nivel} ({self.ano_escolar})"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'nivel'], name='unique_student_nivel')
        ]

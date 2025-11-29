from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from usuarios.models import Usuario
from jardines.models import Jardin



class Niño(models.Model):
    EPS_CHOICES = [
        ('COOSALUD EPS-S', 'COOSALUD EPS-S'),
        ('NUEVA EPS', 'NUEVA EPS'),
        ('MUTUAL SER', 'MUTUAL SER'),
        ('SALUD MÍA', 'SALUD MÍA'),
        ('ALIANSALUD EPS', 'ALIANSALUD EPS'),
        ('SALUD TOTAL EPS S.A.', 'SALUD TOTAL EPS S.A.'),
        ('EPS SANITAS', 'EPS SANITAS'),
        ('EPS SURA', 'EPS SURA'),
        ('FAMISANAR', 'FAMISANAR'),
        ('SERVICIO OCCIDENTAL DE SALUD EPS SOS', 'SERVICIO OCCIDENTAL DE SALUD EPS SOS'),
        ('COMFENALCO VALLE', 'COMFENALCO VALLE'),
        ('COMPENSAR EPS', 'COMPENSAR EPS'),
        ('EPM - EMPRESAS PUBLICAS DE MEDELLIN', 'EPM - EMPRESAS PUBLICAS DE MEDELLIN'),
        ('FONDO DE PASIVO SOCIAL DE FERROCARRILES NACIONALES DE COLOMBIA', 'FONDO DE PASIVO SOCIAL DE FERROCARRILES NACIONALES DE COLOMBIA'),
        ('CAJACOPI ATLANTICO', 'CAJACOPI ATLANTICO'),
        ('CAPRESOCA', 'CAPRESOCA'),
        ('COMFACHOCO', 'COMFACHOCO'),
        ('COMFAORIENTE', 'COMFAORIENTE'),
        ('EPS FAMILIAR DE COLOMBIA', 'EPS FAMILIAR DE COLOMBIA'),
        ('ASMET SALUD', 'ASMET SALUD'),
        ('EMSSANAR E.S.S.', 'EMSSANAR E.S.S.'),
        ('CAPITAL SALUD EPS-S', 'CAPITAL SALUD EPS-S'),
        ('SAVIA SALUD EPS', 'SAVIA SALUD EPS'),
        ('DUSAKAWI EPSI', 'DUSAKAWI EPSI'),
        ('ASOCIACION INDIGENA DEL CAUCA EPSI', 'ASOCIACION INDIGENA DEL CAUCA EPSI'),
        ('ANAS WAYUU EPSI', 'ANAS WAYUU EPSI'),
        ('MALLAMAS EPSI', 'MALLAMAS EPSI'),
        ('PIJAOS SALUD EPSI', 'PIJAOS SALUD EPSI'),
    ]
    
    registro = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=150)
    fecha_nacimiento = models.DateField()
    tipo_sangre = models.CharField(max_length=3)
    ciudad_nacimiento = models.CharField(max_length=100)
    acudiente = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name='niños')
    telefono = models.CharField(max_length=15)
    direccion = models.TextField()
    eps = models.CharField(max_length=100, choices=EPS_CHOICES)
    jardin = models.ForeignKey(
        Jardin, on_delete=models.CASCADE, related_name='niños')
    fecha_registro = models.DateField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.nombre

    def clean(self):
        edad = (timezone.now().date() - self.fecha_nacimiento).days // 365
        if edad >= 6:
            raise ValidationError(
                "El niño no puede tener más de 6 años al ser registrado.")

    def get_edad(self):
        return (timezone.now().date() - self.fecha_nacimiento).days // 365


class Asistencia(models.Model):
    fecha = models.DateField()
    niño = models.ForeignKey(
        Niño, on_delete=models.CASCADE, related_name='asistencias')
    estado_nino = models.CharField(max_length=20, choices=[
        ('Enfermo', 'Enfermo'),
        ('Sano', 'Sano'),
        ('Decaído', 'Decaído')
    ])

    def __str__(self):
        return f"{self.fecha} - {self.niño.nombre} - {self.niño.jardin}"

    def clean(self):
        # Validación para asegurarse que el registro de asistencia sea entre 8 y 10 AM
        now = timezone.now()
        if not (now.hour >= 8 and now.hour <= 10):
            raise ValidationError(
                "El llamado de lista debe registrarse entre las 8 y las 10 de la mañana.")

        if self.estado_nino == 'Enfermo':
            # Lógica para reportar al administrador si el niño está enfermo
            pass


class AvanceAcademico(models.Model):
    niño = models.ForeignKey(
        Niño, on_delete=models.CASCADE, related_name='avances_academicos')
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
        return f"{self.niño.nombre} - {self.nivel} ({self.ano_escolar})"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['niño', 'nivel'], name='unique_nino_nivel')
        ]

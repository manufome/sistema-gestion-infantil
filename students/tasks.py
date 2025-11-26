from background_task import background
from django.utils import timezone
from .models import Student
from .utils import enviar_correo_cumpleaños, notificar_guardian

@background(schedule=20)
def verificar_cumpleaños_diariamente():
    print("Verificando cumpleaños...")
    hoy = timezone.now().date()
    students_cumpleaños = Student.objects.filter(
        fecha_nacimiento__month=hoy.month,
        fecha_nacimiento__day=hoy.day
    )
    print(f"Estudiantes con cumpleaños hoy: {students_cumpleaños}")
    for student in students_cumpleaños:
        enviar_correo_cumpleaños(student)
        if student.get_edad() >= 5:
            notificar_guardian(student)
    

# python manage.py schedule_tasks
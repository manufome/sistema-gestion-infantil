from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from students.models import Attendance, Student
from institutions.models import Institution
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

@login_required
@user_passes_test(lambda user: user.is_administrador())
def reportes_general(request):
    # Aquí obtenemos los datos para todos los reportes
    fecha_fin = timezone.now().date()
    # Ajustamos la fecha de inicio para excluir sábados y domingos
    fecha_inicio = fecha_fin - timedelta(days=fecha_fin.weekday())
    if fecha_inicio > fecha_fin:
        fecha_inicio -= timedelta(days=7)
    
    # Obtenemos solo las instituciones aprobadas
    institutions_aprobadas = Institution.get_aprobados()
    
    # Datos para reporte_semanal_asistencia
    asistencias = Attendance.objects.filter(
        fecha__range=[fecha_inicio, fecha_fin], 
        fecha__week_day__range=[2, 6],
        student__institution__in=institutions_aprobadas
    )
    
    reporte_asistencia = {}
    for institution in institutions_aprobadas:
        asistencias_institution = asistencias.filter(student__institution=institution)
        total_asistencias = asistencias_institution.values('fecha').distinct().count()
        
        # Obtener todos los estudiantes de la institución
        students = Student.objects.filter(institution=institution)
        
        asistencias_por_student = {}
        for student in students:
            nombre = student.nombre + ' ' + student.guardian.last_name
            asistencias_semana = []
            for dia in range(5):  # Solo de lunes a viernes
                fecha = fecha_inicio + timedelta(days=dia)
                asistencia = asistencias_institution.filter(student=student, fecha=fecha).first()
                if asistencia:
                    asistencias_semana.append(asistencia.estado_nino)
                else:
                    asistencias_semana.append('No registrado')
            asistencias_por_student[nombre] = asistencias_semana
        
        reporte_asistencia[institution.nombre] = {
            'total_asistencias': total_asistencias,
            'asistencias_por_niño': asistencias_por_student
        }

    # Datos para reporte_inasistencias_enfermedad
    inasistencias = Attendance.objects.filter(
        fecha__range=[fecha_inicio, fecha_fin],
        fecha__week_day__range=[2, 6],
        estado_nino='Enfermo',
        student__institution__in=institutions_aprobadas
    ).values('student__institution__nombre').annotate(total=Count('id'))
    
    # Datos para reporte_niños_por_jardin
    institutions_con_students = institutions_aprobadas.annotate(total_niños=Count('students'))
    
    # Datos para reporte_jardines_no_aprobados
    institutions_no_aprobadas = Institution.objects.filter(estado__in=['En trámite', 'Negado'])
    
    hay_jardines_no_aprobados = institutions_no_aprobadas.exists()
    
    context = {
        'reporte': reporte_asistencia,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'inasistencias': inasistencias,
        'jardines': institutions_con_students,
        'jardines_no_aprobados': institutions_no_aprobadas,
        'hay_jardines_no_aprobados': hay_jardines_no_aprobados,
    }
    return render(request, 'reportes/reportes_general.html', context)
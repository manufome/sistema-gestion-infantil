from django.db import IntegrityError
from .models import Student, AcademicProgress
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from datetime import date, datetime
from django.shortcuts import get_object_or_404, render, redirect
from .models import Student, Attendance, AcademicProgress
from institutions.models import Institution
from .forms import StudentForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from users.models import Actividad
from django.db.models import Count

@login_required
@user_passes_test(lambda user: user.is_administrador())
def lista_students(request):
    students = Student.objects.all()
    urls = {
        'crear': 'crear_student',
        'editar': 'editar_student',
        'eliminar': 'eliminar_student',
    }
    objects = []
    for student in students:
        objects.append({
            'id': student.pk,
            'Registro': student.registro,
            'Nombre': student.nombre,
            'Edad': student.get_edad(),
            'Tipo de Sangre': student.tipo_sangre,
            'Ciudad de Nacimiento': student.ciudad_nacimiento,
            'Guardian': student.guardian,
            'Teléfono': student.telefono,
            'Dirección': student.direccion,
            'EPS': student.eps,
            'Institución': student.institution
        })
    fields = ['Registro', 'Nombre', 'Edad', 'Tipo de Sangre',
              'Ciudad de Nacimiento', 'Guardian', 'Teléfono', 'Dirección', 'EPS', 'Institución']
    return render(request, 'crud/form_listar.html', {'objects': objects, 'urls': urls, 'title': 'Lista de Estudiantes', 'nuevo': 'Crear Nuevo Estudiante', 'fields': fields})


@login_required
@user_passes_test(lambda user: user.is_administrador())
def crear_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            Actividad.objects.create(
                tipo='creacion',
                descripcion=f'Nuevo estudiante registrado: {student.nombre} en la institución {student.institution}',
                icono='fa-child',
                content_type=ContentType.objects.get_for_model(student),
                object_id=student.id
            )
            messages.success(request, f'Estudiante {student.nombre} registrado exitosamente en la institución {student.institution}')
            return redirect('students:lista_students')
    else:
        form = StudentForm()

    return render(request, 'crud/form_crear.html', {'form': form, 'title': 'Crear Estudiante', "back_url": 'lista_students'})


@login_required
@user_passes_test(lambda user: user.is_administrador())
def editar_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            student = form.save()
            cambios = form.changed_data
            Actividad.objects.create(
                tipo='edicion',
                descripcion=f'Estudiante editado: {student.nombre}. Campos modificados: {", ".join(cambios)}',
                icono='fa-child',
                content_type=ContentType.objects.get_for_model(student),
                object_id=student.id
            )
            messages.success(request, f'Información de {student.nombre} actualizada exitosamente. Campos modificados: {", ".join(cambios)}')
            return redirect('students:lista_students')
    else:
        form = StudentForm(instance=student)

    return render(request, 'crud/form_editar.html', {'form': form, 'title': 'Editar Estudiante', 'back_url': 'lista_students'})


@login_required
@user_passes_test(lambda user: user.is_administrador())
def eliminar_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        nombre = student.nombre
        institution = student.institution
        Actividad.objects.create(
            tipo='eliminacion',
            descripcion=f'Estudiante eliminado: {nombre} de la institución {institution}',
            icono='fa-child',
            content_type=ContentType.objects.get_for_model(student),
            object_id=student.id
        )
        student.delete()
        messages.success(request, f'Estudiante {nombre} eliminado exitosamente de la institución {institution}')
        return redirect('lista_students')

    return render(request, 'crud/form_eliminar.html', {'model': student, 'title': 'Eliminar Estudiante', 'back_url': 'lista_students'})


@login_required
@user_passes_test(lambda user: user.is_teacher())
def asistencia(request):
    institutions = Institution.get_aprobados()
    students = []
    asistencia = []

    if request.htmx:
        search = request.GET.get('search')
        institution_id = request.GET.get('institution_id')
        fecha = request.GET.get('fecha')
        
        if institution_id and fecha:
            students = Student.objects.filter(institution_id=institution_id, institution__estado='Aprobado')
            asistencia = Attendance.objects.filter(fecha=fecha, student__institution_id=institution_id)
            if asistencia.exists():
                students_asistencia = {a.student_id: a.estado_nino for a in asistencia}
                students_data = []
                for student in students:
                    students_data.append({
                        "id": student.id,
                        "nombre": student.nombre + " " + student.guardian.last_name,
                        "edad": student.get_edad(),
                        "estado": students_asistencia.get(student.id, "No asistió")
                    })
                if search:
                    students_data = [student for student in students_data if search.lower() in student['nombre'].lower()]
                return render(request, 'madre/partials/lista_students_asistencia.html', {
                    'niños': students_data,
                    'fecha': fecha,
                    'asistencia_registrada': True,
                })
            else:
                estados = ['Sano', 'Enfermo', 'Decaído', 'No asistió']
                students_data = [{"id": student.id, "nombre": student.nombre + " " + student.guardian.last_name, "edad": student.get_edad()} for student in students]
                return render(request, 'madre/partials/lista_students_asistencia.html', {
                    'niños': students_data,
                    'estados': estados,
                    'fecha': fecha,
                    'asistencia_registrada': False,
                })
        elif search:
            students = Student.objects.filter(nombre__icontains=search)

        estados = ['Sano', 'Enfermo', 'Decaído', 'No asistió']
        students_data = [{"id": student.id, "nombre": student.nombre + " " + student.guardian.last_name, "edad": student.get_edad()} for student in students]
        
        return render(request, 'madre/partials/lista_students_asistencia.html', {
            'niños': students_data, 
            'estados': estados, 
            'fecha': fecha,
        })

    return render(request, 'madre/asistencia.html', {'jardines': institutions, 'niños': students})


@login_required
def registrar_asistencia(request):
    if request.method == 'POST':
        fecha = request.POST.get('fecha')
        students_ids = request.POST.getlist('niños')
        
        for student_id in students_ids:
            estado = request.POST.get(f'estado_{student_id}')
            student = get_object_or_404(Student, pk=student_id)
            
            Attendance.objects.update_or_create(
                student=student,
                fecha=fecha,
                defaults={'estado_nino': estado}
            )
            
        messages.success(request, 'Asistencia registrada correctamente')
        return redirect('students:asistencia')


@login_required
@user_passes_test(lambda user: user.is_teacher())
def avance_academico(request):
    notas = [
        ('S', 'Superior'),
        ('A', 'Alto'),
        ('B', 'Bajo')
    ]
    niveles = ['Prenatal', 'Natal', 'Párvulo', 'Pre-jardín', 'Jardín']
    students = Student.objects.all()
    institutions = Institution.get_aprobados()
    if request.method == 'POST':
        student_id = request.POST.get('niño_id')
        date = request.POST.get('date')
        nivel = request.POST.get('nivel')
        nota = request.POST.get('nota')
        comments = request.POST.get('comments')

        try:
            student = get_object_or_404(Student, pk=student_id)
            avance_academico = AcademicProgress.objects.create(
                student=student,
                fecha_entrega=date,
                nivel=nivel,
                notas=nota,
                descripcion=comments,
                ano_escolar=datetime.strptime(date, "%Y-%m-%d").year
            )
            avance_academico.save()
            messages.success(request, 'Avance académico registrado con éxito')
            return redirect('students:avance_academico')
        except IntegrityError:
            messages.error(
                request, 'El estudiante ya tiene un avance académico registrado para este nivel.')
            return redirect('students:avance_academico')
        except Exception as e:
            messages.error(
                request, f'Error al registrar el avance académico: {e}')
            return redirect('students:avance_academico')

    if request.htmx:
        institution_id = request.GET.get('jardin')
        student_id = request.GET.get('niño_id')
        
        if institution_id:
            students = Student.objects.filter(institution_id=institution_id)
            return render(request, 'madre/partials/select_students.html', {'niños': students})
        
        if student_id:
            student = get_object_or_404(Student, pk=student_id)
            avance_academico = AcademicProgress.objects.filter(student=student)
            return render(request, 'madre/partials/info_student_avance.html', {'avance_academico': avance_academico, 'niño': student})

    return render(request, 'madre/avance_academico.html', {'niños': students, 'notas': notas, 'niveles': niveles, 'jardines': institutions})

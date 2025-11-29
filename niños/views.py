from django.db import IntegrityError
from .models import Niño, AvanceAcademico
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from datetime import date, datetime, time
from django.shortcuts import get_object_or_404, render, redirect
from .models import Niño, Asistencia, AvanceAcademico
from jardines.models import Jardin
from .forms import NiñoForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from usuarios.models import Actividad
from django.db.models import Count

@login_required
@user_passes_test(lambda user: user.is_administrador())
def lista_niños(request):
    niños = Niño.objects.all()
    urls = {
        'crear': 'crear_niño',
        'editar': 'editar_niño',
        'eliminar': 'eliminar_niño',
    }
    objects = []
    for niño in niños:
        objects.append({
            'id': niño.pk,
            'Registro': niño.registro,
            'Nombre': niño.nombre,
            'Edad': niño.get_edad(),
            'Tipo de Sangre': niño.tipo_sangre,
            'Ciudad de Nacimiento': niño.ciudad_nacimiento,
            'Acudiente': niño.acudiente,
            'Teléfono': niño.telefono,
            'Dirección': niño.direccion,
            'EPS': niño.eps,
            'Jardín': niño.jardin
        })
    fields = ['Registro', 'Nombre', 'Edad', 'Tipo de Sangre',
              'Ciudad de Nacimiento', 'Acudiente', 'Teléfono', 'Dirección', 'EPS', 'Jardín']
    return render(request, 'crud/form_listar.html', {'objects': objects, 'urls': urls, 'title': 'Lista de Niños', 'nuevo': 'Crear Nuevo Niño', 'fields': fields})


@login_required
@user_passes_test(lambda user: user.is_administrador())
def crear_niño(request):
    if request.method == 'POST':
        form = NiñoForm(request.POST)
        if form.is_valid():
            niño = form.save()
            Actividad.objects.create(
                tipo='creacion',
                descripcion=f'Nuevo niño registrado: {niño.nombre} en el jardín {niño.jardin}',
                icono='fa-child',
                content_type=ContentType.objects.get_for_model(niño),
                object_id=niño.id
            )
            messages.success(request, f'Niño {niño.nombre} registrado exitosamente en el jardín {niño.jardin}')
            return redirect('niños:lista_niños')
    else:
        form = NiñoForm()

    return render(request, 'crud/form_crear.html', {'form': form, 'title': 'Crear Niño', "back_url": 'lista_niños'})


@login_required
@user_passes_test(lambda user: user.is_administrador())
def editar_niño(request, pk):
    niño = get_object_or_404(Niño, pk=pk)
    if request.method == 'POST':
        form = NiñoForm(request.POST, instance=niño)
        if form.is_valid():
            niño = form.save()
            cambios = form.changed_data
            Actividad.objects.create(
                tipo='edicion',
                descripcion=f'Niño editado: {niño.nombre}. Campos modificados: {", ".join(cambios)}',
                icono='fa-child',
                content_type=ContentType.objects.get_for_model(niño),
                object_id=niño.id
            )
            messages.success(request, f'Información de {niño.nombre} actualizada exitosamente. Campos modificados: {", ".join(cambios)}')
            return redirect('niños:lista_niños')
    else:
        form = NiñoForm(instance=niño)

    return render(request, 'crud/form_editar.html', {'form': form, 'title': 'Editar Niño', 'back_url': 'lista_niños'})


@login_required
@user_passes_test(lambda user: user.is_administrador())
def eliminar_niño(request, pk):
    niño = get_object_or_404(Niño, pk=pk)
    if request.method == 'POST':
        nombre = niño.nombre
        jardin = niño.jardin
        Actividad.objects.create(
            tipo='eliminacion',
            descripcion=f'Niño eliminado: {nombre} del jardín {jardin}',
            icono='fa-child',
            content_type=ContentType.objects.get_for_model(niño),
            object_id=niño.id
        )
        niño.delete()
        messages.success(request, f'Niño {nombre} eliminado exitosamente del jardín {jardin}')
        return redirect('lista_niños')

    return render(request, 'crud/form_eliminar.html', {'model': niño, 'title': 'Eliminar Niño', 'back_url': 'lista_niños'})


@login_required
@user_passes_test(lambda user: user.is_madre_comunitaria())
def asistencia(request):
    jardines = Jardin.get_aprobados()
    niños = []
    asistencia = []

    if request.htmx:
        search = request.GET.get('search')
        jardin_id = request.GET.get('jardin_id')
        fecha = request.GET.get('fecha')
        
        if jardin_id and fecha:
            niños = Niño.objects.filter(jardin_id=jardin_id, jardin__estado='Aprobado')
            asistencia = Asistencia.objects.filter(fecha=fecha, niño__jardin_id=jardin_id)
            if asistencia.exists():
                niños_asistencia = {a.niño_id: a.estado_nino for a in asistencia}
                niños_data = []
                for niño in niños:
                    niños_data.append({
                        "id": niño.id,
                        "nombre": niño.nombre + " " + niño.acudiente.last_name,
                        "edad": niño.get_edad(),
                        "estado": niños_asistencia.get(niño.id, "No asistió")
                    })
                if search:
                    niños_data = [niño for niño in niños_data if search.lower() in niño['nombre'].lower()]
                return render(request, 'madre/partials/lista_niños_asistencia.html', {
                    'niños': niños_data,
                    'fecha': fecha,
                    'asistencia_registrada': True,
                })
            else:
                estados = ['Sano', 'Enfermo', 'Decaído', 'No asistió']
                niños_data = [{"id": niño.id, "nombre": niño.nombre + " " + niño.acudiente.last_name, "edad": niño.get_edad()} for niño in niños]
                return render(request, 'madre/partials/lista_niños_asistencia.html', {
                    'niños': niños_data,
                    'estados': estados,
                    'fecha': fecha,
                    'asistencia_registrada': False,
                })
        elif search:
            niños = Niño.objects.filter(nombre__icontains=search)

        estados = ['Sano', 'Enfermo', 'Decaído', 'No asistió']
        niños_data = [{"id": niño.id, "nombre": niño.nombre + " " + niño.acudiente.last_name, "edad": niño.get_edad()} for niño in niños]
        
        return render(request, 'madre/partials/lista_niños_asistencia.html', {
            'niños': niños_data, 
            'estados': estados, 
            'fecha': fecha,
        })

    return render(request, 'madre/asistencia.html', {'jardines': jardines, 'niños': niños})


@login_required
@user_passes_test(lambda user: user.is_madre_comunitaria())
def registrar_asistencia(request):
    if request.method == 'POST':
        # Validar que sea el día actual
        fecha_str = request.POST.get('fecha')
        if fecha_str:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        else:
            fecha = date.today()
        
        # Validar que la fecha sea hoy
        if fecha != date.today():
            messages.error(request, 'Solo se puede registrar asistencia para el día de hoy')
            return redirect('asistencia')
        
        # Validar horario (8:00 AM - 10:00 AM)
        hora_actual = datetime.now().time()
        hora_inicio = time(8, 0)  # 8:00 AM
        hora_fin = time(10, 0)    # 10:00 AM
        
        if not (hora_inicio <= hora_actual <= hora_fin):
            messages.error(request, 'La asistencia solo puede registrarse entre las 8:00 AM y las 10:00 AM')
            return redirect('asistencia')
        
        niños = request.POST.getlist('niños')
        for niño_id in niños:
            niño = get_object_or_404(Niño, pk=niño_id)
            estado = request.POST.get(f'estado_{niño_id}')
            asistencia = Asistencia.objects.create(
                fecha=fecha, niño=niño, estado_nino=estado)
            asistencia.save()
            if estado == 'Enfermo':
                Actividad.objects.create(
                    tipo='otro',
                    descripcion=f'El niño {niño.nombre} {niño.acudiente.last_name } del jardín {niño.jardin} se encuentra enfermo',
                    icono='fa-child',
                    content_type=ContentType.objects.get_for_model(niño),
                    object_id=niño.id
                )
        messages.success(request, 'Asistencia registrada con éxito')
        return redirect('asistencia')
    messages.error(request, 'Error al registrar la asistencia')
    return redirect('asistencia')


@login_required
@user_passes_test(lambda user: user.is_madre_comunitaria())
def avance_academico(request):
    notas = [
        ('S', 'Superior'),
        ('A', 'Alto'),
        ('B', 'Bajo')
    ]
    niveles = ['Prenatal', 'Natal', 'Párvulo', 'Pre-jardín', 'Jardín']
    niños = Niño.objects.all()
    jardines = Jardin.get_aprobados()
    if request.method == 'POST':
        niño_id = request.POST.get('niño_id')
        date = request.POST.get('date')
        nivel = request.POST.get('nivel')
        nota = request.POST.get('nota')
        comments = request.POST.get('comments')

        try:
            niño = get_object_or_404(Niño, pk=niño_id)
            avance_academico = AvanceAcademico.objects.create(
                niño=niño,
                fecha_entrega=date,
                nivel=nivel,
                notas=nota,
                descripcion=comments,
                ano_escolar=datetime.strptime(date, "%Y-%m-%d").year
            )
            avance_academico.save()
            messages.success(request, 'Avance académico registrado con éxito')
            return redirect('avance_academico')
        except IntegrityError:
            messages.error(
                request, 'El niño ya tiene un avance académico registrado para este nivel.')
            return redirect('avance_academico')
        except Exception as e:
            messages.error(
                request, f'Error al registrar el avance académico: {e}')
            return redirect('avance_academico')

    if request.htmx:
        jardin_id = request.GET.get('jardin')
        niño_id = request.GET.get('niño_id')
        
        if jardin_id:
            niños = Niño.objects.filter(jardin_id=jardin_id)
            return render(request, 'madre/partials/select_niños.html', {'niños': niños})
        elif 'jardin' in request.GET and not jardin_id:
             return render(request, 'madre/partials/select_niños.html', {'niños': []})
        
        if niño_id:
            niño = get_object_or_404(Niño, pk=niño_id)
            avance_academico = AvanceAcademico.objects.filter(niño=niño)
            return render(request, 'madre/partials/info_niño_avance.html', {'avance_academico': avance_academico, 'niño': niño})

    return render(request, 'madre/avance_academico.html', {'niños': [], 'notas': notas, 'niveles': niveles, 'jardines': jardines})

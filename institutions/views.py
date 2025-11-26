from django.shortcuts import render, redirect, get_object_or_404
from .models import Institution
from .forms import InstitutionForm
from django.contrib.contenttypes.models import ContentType
from users.models import Actividad
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

@login_required
@user_passes_test(lambda user: user.is_administrador())
def lista_institutions(request):
    institutions = Institution.objects.all()
    urls = {
        'crear': 'crear_institution',
        'editar': 'editar_institution',
        'eliminar': 'eliminar_institution',
    }
    objects = []
    for institution in institutions:
        objects.append({
            'Nombre': institution.nombre,
            'Dirección': institution.direccion,
            'Estado': institution.estado,
            'id': institution.pk
        })
    fields = ['Nombre', 'Dirección', 'Estado']
    return render(request, 'crud/form_listar.html', {'objects': objects, 'urls': urls, 'title': 'Lista de Instituciones', 'nuevo': 'Crear Nueva Institución', 'fields': fields})


@login_required
@user_passes_test(lambda user: user.is_administrador())
def crear_institution(request):
    if request.method == 'POST':
        form = InstitutionForm(request.POST)
        if form.is_valid():
            institution = form.save()
            Actividad.objects.create(
                tipo='creacion',
                descripcion=f'Nueva institución creada: {institution.nombre} con estado {institution.estado}',
                icono='fa-school',
                content_type=ContentType.objects.get_for_model(institution),
                object_id=institution.id
            )
            messages.success(request, f'Institución {institution.nombre} creada exitosamente con estado {institution.estado}')
            return redirect('lista_institutions')
    else:
        form = InstitutionForm()

    return render(request, 'crud/form_crear.html', {'form': form, 'title': 'Crear Institución', 'back_url': 'lista_institutions'})


@login_required
@user_passes_test(lambda user: user.is_administrador())
def editar_institution(request, pk):
    institution = get_object_or_404(Institution, pk=pk)
    if request.method == 'POST':
        form = InstitutionForm(request.POST, instance=institution)
        if form.is_valid():
            institution = form.save()
            cambios = form.changed_data
            Actividad.objects.create(
                tipo='edicion',
                descripcion=f'Institución editada: {institution.nombre}. Campos modificados: {", ".join(cambios)}',
                icono='fa-school',
                content_type=ContentType.objects.get_for_model(institution),
                object_id=institution.id
            )
            if 'estado' in cambios:
                if institution.estado in ['En trámite', 'Negado']:
                    messages.warning(request, f'La institución {institution.nombre} ha sido puesta bajo supervisión con estado {institution.estado}')
                else:
                    messages.success(request, f'La institución {institution.nombre} ahora tiene el estado {institution.estado}')
            else:
                messages.success(request, f'Institución {institution.nombre} actualizada exitosamente. Campos modificados: {", ".join(cambios)}')
            return redirect('lista_institutions')
    else:
        form = InstitutionForm(instance=institution)

    return render(request, 'crud/form_editar.html', {'form': form, 'title': 'Editar Institución', 'back_url': 'lista_institutions'})


@login_required
@user_passes_test(lambda user: user.is_administrador())
def eliminar_institution(request, pk):
    institution = get_object_or_404(Institution, pk=pk)
    if request.method == 'POST':
        nombre = institution.nombre
        estado = institution.estado
        Actividad.objects.create(
            tipo='eliminacion',
            descripcion=f'Institución eliminada: {nombre} con estado {estado}',
            icono='fa-school',
            content_type=ContentType.objects.get_for_model(institution),
            object_id=institution.id
        )
        institution.delete()
        messages.success(request, f'Institución {nombre} con estado {estado} eliminada exitosamente')
        return redirect('lista_institutions')

    return render(request, 'crud/form_eliminar.html', {'model': institution, 'title': 'Eliminar Institución', 'back_url': 'lista_institutions'})

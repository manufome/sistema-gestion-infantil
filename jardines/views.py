from django.shortcuts import render, redirect, get_object_or_404
from .models import Jardin
from .forms import JardinForm
from django.contrib.contenttypes.models import ContentType
from usuarios.models import Actividad
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

@login_required
@user_passes_test(lambda user: user.is_administrador())
def lista_jardines(request):
    jardines = Jardin.objects.all()
    urls = {
        'crear': 'crear_jardin',
        'editar': 'editar_jardin',
        'eliminar': 'eliminar_jardin',
    }
    objects = []
    for jardin in jardines:
        objects.append({
            'Nombre': jardin.nombre,
            'Dirección': jardin.direccion,
            'Estado': jardin.estado,
            'id': jardin.pk
        })
    fields = ['Nombre', 'Dirección', 'Estado']
    return render(request, 'crud/form_listar.html', {'objects': objects, 'urls': urls, 'title': 'Lista de Jardines', 'nuevo': 'Crear Nuevo Jardín', 'fields': fields})


@login_required
@user_passes_test(lambda user: user.is_administrador())
def crear_jardin(request):
    if request.method == 'POST':
        form = JardinForm(request.POST)
        if form.is_valid():
            jardin = form.save()
            Actividad.objects.create(
                tipo='creacion',
                descripcion=f'Nuevo jardín creado: {jardin.nombre} con estado {jardin.estado}',
                icono='fa-school',
                content_type=ContentType.objects.get_for_model(jardin),
                object_id=jardin.id
            )
            messages.success(request, f'Jardín {jardin.nombre} creado exitosamente con estado {jardin.estado}')
            return redirect('lista_jardines')
    else:
        form = JardinForm()

    return render(request, 'crud/form_crear.html', {'form': form, 'title': 'Crear Jardín', 'back_url': 'lista_jardines'})


@login_required
@user_passes_test(lambda user: user.is_administrador())
def editar_jardin(request, pk):
    jardin = get_object_or_404(Jardin, pk=pk)
    if request.method == 'POST':
        form = JardinForm(request.POST, instance=jardin)
        if form.is_valid():
            jardin = form.save()
            cambios = form.changed_data
            
            # Crear mensaje específico basado en el cambio de estado
            if 'estado' in cambios:
                if jardin.estado == 'Aprobado':
                    descripcion_actividad = f'El jardín {jardin.nombre} ha sido aprobado'
                    mensaje_usuario = f'El jardín {jardin.nombre} ha sido aprobado exitosamente'
                    tipo_mensaje = 'success'
                elif jardin.estado == 'Negado':
                    descripcion_actividad = f'El jardín {jardin.nombre} ha sido negado'
                    mensaje_usuario = f'El jardín {jardin.nombre} ha sido negado'
                    tipo_mensaje = 'warning'
                elif jardin.estado == 'En trámite':
                    descripcion_actividad = f'El jardín {jardin.nombre} ha sido puesto en trámite'
                    mensaje_usuario = f'El jardín {jardin.nombre} ha sido puesto en trámite'
                    tipo_mensaje = 'warning'
                else:
                    descripcion_actividad = f'El jardín {jardin.nombre} cambió su estado a {jardin.estado}'
                    mensaje_usuario = f'El jardín {jardin.nombre} ahora tiene el estado {jardin.estado}'
                    tipo_mensaje = 'success'
            else:
                descripcion_actividad = f'Jardín editado: {jardin.nombre}. Campos modificados: {", ".join(cambios)}'
                mensaje_usuario = f'Jardín {jardin.nombre} actualizado exitosamente. Campos modificados: {", ".join(cambios)}'
                tipo_mensaje = 'success'
            
            # Crear actividad con descripción específica
            Actividad.objects.create(
                tipo='edicion',
                descripcion=descripcion_actividad,
                icono='fa-school',
                content_type=ContentType.objects.get_for_model(jardin),
                object_id=jardin.id
            )
            
            # Mostrar mensaje al usuario
            if tipo_mensaje == 'warning':
                messages.warning(request, mensaje_usuario)
            else:
                messages.success(request, mensaje_usuario)
                
            return redirect('lista_jardines')
    else:
        form = JardinForm(instance=jardin)

    return render(request, 'crud/form_editar.html', {'form': form, 'title': 'Editar Jardín', 'back_url': 'lista_jardines'})


@login_required
@user_passes_test(lambda user: user.is_administrador())
def eliminar_jardin(request, pk):
    jardin = get_object_or_404(Jardin, pk=pk)
    if request.method == 'POST':
        nombre = jardin.nombre
        estado = jardin.estado
        Actividad.objects.create(
            tipo='eliminacion',
            descripcion=f'Jardín eliminado: {nombre} con estado {estado}',
            icono='fa-school',
            content_type=ContentType.objects.get_for_model(jardin),
            object_id=jardin.id
        )
        jardin.delete()
        messages.success(request, f'Jardín {nombre} con estado {estado} eliminado exitosamente')
        return redirect('lista_jardines')

    return render(request, 'crud/form_eliminar.html', {'model': jardin, 'title': 'Eliminar Jardín', 'back_url': 'lista_jardines'})

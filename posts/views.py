from django.shortcuts import render, get_object_or_404, redirect
from .models import Post
from .forms import PostForm
from django.contrib.contenttypes.models import ContentType
from users.models import Actividad
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test


@login_required
@user_passes_test(lambda user: user.is_administrador())
def lista_posts(request):
    posts = Post.objects.all()
    urls = {
        'crear': 'crear_post',
        'editar': 'editar_post',
        'eliminar': 'eliminar_post',
    }
    objects = []
    for post in posts:
        objects.append({
            'Título': post.titulo,
            'Descripción': post.descripcion,
            'Fecha de Publicación': post.fecha_publicacion,
            'Archivo': post.archivo.name,
            'url_descargar': post.archivo.url,
            'id': post.pk
        })
    fields = ['Título', 'Descripción', 'Fecha de Publicación', 'Archivo']
    return render(request, 'crud/form_listar.html', {'objects': objects, 'urls': urls, 'title': 'Lista de Publicaciones', 'nuevo': 'Crear Nueva Publicación', 'fields': fields})


@login_required
@user_passes_test(lambda user: user.is_administrador())
def crear_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save()
            Actividad.objects.create(
                tipo='creacion',
                descripcion=f'Nueva publicación creada: "{post.titulo}" el {post.fecha_publicacion}',
                icono='fa-file-alt',
                content_type=ContentType.objects.get_for_model(post),
                object_id=post.id
            )
            messages.success(request, f'Publicación "{post.titulo}" creada exitosamente el {post.fecha_publicacion}')
            return redirect('lista_posts')
    else:
        form = PostForm()

    return render(request, 'publicaciones/crear.html', {'form': form, 'title': 'Crear Publicación', 'back_url': 'lista_posts'})


@login_required
@user_passes_test(lambda user: user.is_administrador())
def editar_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            cambios = form.changed_data
            Actividad.objects.create(
                tipo='edicion',
                descripcion=f'Publicación editada: "{post.titulo}". Campos modificados: {", ".join(cambios)}',
                icono='fa-file-alt',
                content_type=ContentType.objects.get_for_model(post),
                object_id=post.id
            )
            messages.success(request, f'Publicación "{post.titulo}" actualizada exitosamente. Campos modificados: {", ".join(cambios)}')
            return redirect('lista_posts')
    else:
        form = PostForm(instance=post)

    return render(request, 'publicaciones/editar.html', {'form': form, 'title': 'Editar Publicación', 'back_url': 'lista_posts'})


@login_required
@user_passes_test(lambda user: user.is_administrador())
def eliminar_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        titulo = post.titulo
        fecha = post.fecha_publicacion
        archivo = post.archivo
        Actividad.objects.create(
            tipo='eliminacion',
            descripcion=f'Publicación eliminada: "{titulo}" del {fecha}',
            icono='fa-file-alt',
            content_type=ContentType.objects.get_for_model(post),
            object_id=post.id
        )
        if archivo:
            import os
            from django.conf import settings
            ruta_archivo = os.path.join(settings.MEDIA_ROOT, str(archivo))
            if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)
        post.delete()
        messages.success(request, f'Publicación "{titulo}" del {fecha} eliminada exitosamente')
        return redirect('lista_posts')

    return render(request, 'crud/form_eliminar.html', {'model': post, 'title': 'Eliminar Publicación', 'back_url': 'lista_posts'})

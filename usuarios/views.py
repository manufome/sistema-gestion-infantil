from django.contrib.auth import login as auth_login, update_session_auth_hash
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.contrib.auth.models import Group
from .forms import UserRegistrationForm, UsuarioForm
from .models import Usuario, Actividad
from niños.models import Niño, AvanceAcademico
from jardines.models import Jardin
from publicaciones.models import Publicacion
from django.contrib.auth.forms import PasswordChangeForm
from django.utils import timezone
from datetime import timedelta

def home(request):
    return render(request, 'home.html')


def redirect_user_dashboard(user):
    if user.is_administrador():
        return '/admin_dashboard/'
    elif user.is_madre_comunitaria():
        return '/niños/asistencia/'
    elif user.is_acudiente():
        return '/panel_acudiente/'
    else:
        return '/home/'


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            role = request.POST.get('role')
            if role in ['madre_comunitaria', 'acudiente']:
                user.save()
                group_name = 'Madre Comunitaria' if role == 'madre_comunitaria' else 'Acudiente'
                group = Group.objects.get(name=group_name)
                user.groups.add(group)
                auth_login(request, user)
                return redirect(redirect_user_dashboard(user)) 
            else:
                form.add_error('role', 'Rol no válido')
        return JsonResponse({
            'success': False,
            'errors': form.errors
        })
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


class UserLoginView(LoginView):
    template_name = 'registration/login.html'
    next_page = 'home'

    def get_success_url(self):
        return redirect_user_dashboard(self.request.user)


class UserLogoutView(LogoutView):
    next_page = 'home'


@login_required
def dashboard(request):
    return redirect(redirect_user_dashboard(request.user))


@login_required
@user_passes_test(lambda user: user.is_administrador())
def admin_dashboard(request):
    # Obtener datos para el dashboard
    total_niños = Niño.objects.count()
    total_jardines = Jardin.objects.count()
    total_madres_comunitarias = Usuario.objects.filter(groups__name='Madre Comunitaria').count()
    total_acudientes = Usuario.objects.filter(groups__name='Acudiente').count()

    # Calcular nuevos registros en el último mes
    un_mes_atras = timezone.now() - timedelta(days=30)
    nuevos_niños_mes = Niño.objects.filter(fecha_registro__gte=un_mes_atras).count()
    nuevos_jardines = Jardin.objects.filter(fecha_registro__gte=un_mes_atras).count()
    nuevas_madres_comunitarias = Usuario.objects.filter(groups__name='Madre Comunitaria', date_joined__gte=un_mes_atras).count()
    nuevos_acudientes_mes = Usuario.objects.filter(groups__name='Acudiente', date_joined__gte=un_mes_atras).count()

    # Obtener actividades recientes (esto es un ejemplo, ajusta según tus necesidades)
    actividades_recientes = Actividad.objects.all().order_by('-fecha')[:5]

    context = {
        'total_niños': total_niños,
        'total_jardines': total_jardines,
        'total_madres_comunitarias': total_madres_comunitarias,
        'total_acudientes': total_acudientes,
        'nuevos_niños_mes': nuevos_niños_mes,
        'nuevos_jardines': nuevos_jardines,
        'nuevas_madres_comunitarias': nuevas_madres_comunitarias,
        'nuevos_acudientes_mes': nuevos_acudientes_mes,
        'actividades_recientes': actividades_recientes,
        'nuevas_notificaciones': len(actividades_recientes)
    }

    return render(request, 'administrador/admin_dashboard.html', context)


@login_required
@user_passes_test(lambda user: user.is_madre_comunitaria())
def madre_dashboard(request):
    return render(request, 'madre/madre_dashboard.html')


@login_required
@user_passes_test(lambda user: user.is_acudiente())
def acudiente_dashboard(request):
    return render(request, 'acudiente/acudiente_dashboard.html')


@login_required
def redirect_dashboard(request):
    return redirect_user_dashboard(request.user)


@login_required
def user_profile(request):
    return render(request, 'registration/profile.html')


@login_required
def configuration(request):
    password_form = PasswordChangeForm(request.user)
    return render(request, 'configuration.html', {'password_form': password_form})


@login_required
@user_passes_test(lambda user: user.is_administrador())
def lista_usuarios(request):
    usuarios = Usuario.objects.all()
    urls = {
        'crear': 'crear_usuario',
        'editar': 'editar_usuario',
        'eliminar': 'eliminar_usuario',
    }
    objects = []
    for usuario in usuarios:
        roles = usuario.get_roles()
        if usuario.is_administrador() or not roles:
            continue
        roles = ', '.join([rol.name for rol in roles])

        objects.append({
            'Usuario': usuario.username,
            'Nombre': usuario.first_name,
            'Apellido': usuario.last_name,
            'Correo': usuario.email,
            'Roles': roles,
            'id': usuario.pk
        })
    fields = ['Usuario', 'Nombre', 'Apellido', 'Correo', 'Roles']
    return render(request, 'crud/form_listar.html', {'objects': objects, 'urls': urls, 'title': 'Lista de Usuarios', 'nuevo': 'Crear Nuevo Usuario', 'fields': fields})


@login_required
@user_passes_test(lambda user: user.is_administrador())
def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            Actividad.objects.create(
                tipo='creacion',
                descripcion=f'Nuevo usuario creado: {user.username} con rol {user.get_roles()[0].name}',
                icono='fa-user-plus',
                content_type=ContentType.objects.get_for_model(user),
                object_id=user.id
            )
            messages.success(request, f'Usuario {user.username} creado exitosamente con rol {user.get_roles()[0].name}')
            return redirect('lista_usuarios')
    else:
        form = UsuarioForm()
    return render(request, 'crud/form_crear.html', {'form': form, 'title': 'Crear Usuario', 'back_url': 'lista_usuarios'})


@login_required
@user_passes_test(lambda user: user.is_administrador())
def editar_usuario(request, pk):
    usuario = Usuario.objects.get(pk=pk)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            user = form.save()
            cambios = form.changed_data
            Actividad.objects.create(
                tipo='edicion',
                descripcion=f'Usuario editado: {user.username}. Campos modificados: {", ".join(cambios)}',
                icono='fa-user-edit',
                content_type=ContentType.objects.get_for_model(user),
                object_id=user.id
            )
            messages.success(request, f'Usuario {user.username} actualizado exitosamente. Campos modificados: {", ".join(cambios)}')
            return redirect('lista_usuarios')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'crud/form_editar.html', {'form': form, 'title': 'Editar Usuario', 'back_url': 'lista_usuarios'})


@login_required
@user_passes_test(lambda user: user.is_administrador())
def eliminar_usuario(request, pk):
    usuario = Usuario.objects.get(pk=pk)
    if request.method == 'POST':
        username = usuario.username
        rol = usuario.get_roles()[0].name if usuario.get_roles() else "sin rol"
        Actividad.objects.create(
            tipo='eliminacion',
            descripcion=f'Usuario eliminado: {username} con rol {rol}',
            icono='fa-user-minus',
            content_type=ContentType.objects.get_for_model(usuario),
            object_id=usuario.id
        )
        usuario.delete()
        messages.success(request, f'Usuario {username} con rol {rol} eliminado exitosamente')
        return redirect('lista_usuarios')
    return render(request, 'crud/form_eliminar.html', {'model': usuario, 'title': 'Eliminar Usuario', 'back_url': 'lista_usuarios'})


@login_required
@user_passes_test(lambda user: user.is_acudiente())
def panel_acudiente(request):
    user = request.user
    niños = Niño.objects.filter(acudiente=user)
    if request.htmx:
        if request.GET.get('niño'):
            niño = Niño.objects.get(pk=request.GET.get('niño'))
            avances = AvanceAcademico.objects.filter(niño=niño).order_by('-fecha_entrega')
            return render(request, 'acudiente/partials/avance_academico.html', {'avances': avances})
        if request.GET.get('publicacion'):
            publicaciones = Publicacion.objects.all()
            return render(request, 'partials/lista_publicaciones.html', {'publicaciones': publicaciones})
    return render(request, 'acudiente/panel_acudiente.html', {'niños': niños})


@login_required
@user_passes_test(lambda user: user.is_madre_comunitaria())
def publicaciones(request):
    publicaciones = Publicacion.objects.all()
    return render(request, 'madre/publicaciones.html', {'publicaciones': publicaciones})

@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()
        messages.success(request, 'Perfil actualizado exitosamente')
    return redirect('configuration')


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Contraseña actualizada exitosamente')
            return redirect('configuration')
        else:
            messages.error(request, 'Por favor corrija los errores abajo.')
            return render(request, 'configuration.html', {'password_form': form})
    return redirect('configuration')
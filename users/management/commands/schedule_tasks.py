from django.core.management.base import BaseCommand
from background_task.models import Task
from niños.tasks import verificar_cumpleaños_diariamente

class Command(BaseCommand):
    help = 'Programa las tareas de fondo para la aplicación niños'

    def handle(self, *args, **options):
        if not Task.objects.filter(verbose_name="verificar_cumpleaños_diariamente").exists():
            verificar_cumpleaños_diariamente(repeat=Task.DAILY, verbose_name="verificar_cumpleaños_diariamente")
            self.stdout.write(self.style.SUCCESS('Tarea de verificación de cumpleaños programada exitosamente'))
        else:
            self.stdout.write(self.style.WARNING('La tarea de verificación de cumpleaños ya está programada'))
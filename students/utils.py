from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def enviar_correo_cumpleaños(student):
    asunto = f"¡Feliz cumpleaños a {student.nombre}!"
    contexto = {
        'nombre_niño': student.nombre,
        'nombre_acudiente': student.guardian.first_name,
    }
    html_mensaje = render_to_string('emails/feliz_cumpleaños.html', contexto)
    mensaje_plano = strip_tags(html_mensaje)
    try:
        send_mail(
            asunto,
            mensaje_plano,
            settings.EMAIL_HOST_USER,
            [student.guardian.email],
            html_message=html_mensaje,
            fail_silently=False,
        )
        print("Correo enviado con éxito")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")

def notificar_guardian(student):
    asunto = f"Alerta: {student.nombre} cumplirá 6 años el próximo año"
    mensaje = f"El estudiante {student.nombre} cumplirá 6 años el próximo año. Por favor, prepare los documentos necesarios para su traslado a un colegio."
    try:
        send_mail(
            asunto,
            mensaje,
            settings.EMAIL_HOST_USER,
            [student.guardian.email],
            fail_silently=False,
        )
        print(f"Notificación enviada al guardian de {student.nombre}")
    except Exception as e:
        print(f"Error al enviar la notificación: {e}")

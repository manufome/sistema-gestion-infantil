from django.db import models


class Post(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_publicacion = models.DateField()
    archivo = models.FileField(upload_to='posts/') 

    def __str__(self):
        return self.titulo

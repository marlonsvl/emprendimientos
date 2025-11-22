from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField

#from django.contrib.auth.models import User

## https://stackoverflow.com/questions/19130942/whats-the-best-way-to-store-a-phone-number-in-django-models
from phonenumber_field.modelfields import PhoneNumberField

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = PhoneNumberField(blank=True, region="EC")
    address = models.CharField(blank=True, max_length=500)
    pic = models.URLField(default='https://picsum.photos/300/30', blank=True)






class Establecimiento(models.Model):
    ACTIVE_CHOICES = [
        ("Sí", "Sí"),
        ("No", "No")
    ]

    LOCAL_CHOICES = [
        ("Propio", "Propio"),
        ("Arrendado", "Arrendado"),
        ("Otro", "Otro"),
    ]
    nombre = models.CharField(max_length=400)
    parroquia = models.CharField(max_length=100)
    #fecha = models.DateTimeField('fecha', auto_now_add=True)
    sector = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(max_length=254)
    propietario = models.CharField(max_length=200)
    tipo_turismo = models.CharField(max_length=200, default="No especificado")
    experiencia = models.IntegerField(default=0)
    asociacion = models.CharField(max_length=20,  default='No')
    ruc = models.CharField(max_length=100,  default='No')
    estado_local = models.CharField(max_length=20, choices=LOCAL_CHOICES, default='Propio')
    servicios_produccion = models.CharField(max_length=1000)
    licencia_gad_loja = models.CharField(max_length=100,  default='No')
    arcsa = models.CharField(max_length=100,  default='No')
    turismo = models.CharField(max_length=100, default='No')
    equipos = models.CharField(max_length=1000)
    pagina_web = models.URLField(max_length=500,  default='No')
    facebook = models.CharField(max_length=500,  default='No')
    instagram = models.CharField(max_length=500,   default='No')
    tiktok = models.CharField(max_length=500, default='No')
    whatsapp = models.CharField(max_length=500, default='No')
    tipo = models.CharField(max_length=100) 
    mesas = models.IntegerField(default=0)
    plazas = models.IntegerField(default=0)
    banio = models.CharField(max_length=2, choices=ACTIVE_CHOICES)
    complementarios = models.CharField(max_length=1000)
    oferta = models.CharField(max_length=600)
    menu = models.TextField(max_length=1200, null=True)
    tipo_servicio = models.CharField(max_length=400)
    precio_promedio = models.DecimalField(
        decimal_places=2, max_digits=10)
    procesos = models.CharField(max_length=400)
    materia_prima = models.CharField(max_length=400)
    proveedores = models.CharField(max_length=400)
    numero_proveedores = models.IntegerField()
    numero_mujeres = models.IntegerField(default=0)
    numero_hombres = models.IntegerField(default=0)
    tiempo_trabajando = models.IntegerField(default=0)
    personal_capacitado = models.CharField(max_length=2, choices=ACTIVE_CHOICES)
    frecuencia_capacitacion = models.CharField(max_length=200) 
    dependencia_ingresos = models.CharField(max_length=200)
    genero = models.CharField(max_length=20, choices=[("Femenino", "Femenino"), ("Masculino", "Masculino"), ("Otro", "Otro")], default="otro")
    nivel_educacion = models.CharField(max_length=200, default="No especificado")
    edad = models.IntegerField(default=0)
    estado_civil = models.CharField(max_length=200)
    longitude = models.DecimalField(max_digits=9, decimal_places=6) # x
    latitude = models.DecimalField(max_digits=9, decimal_places=6) # y
    horario = models.CharField(max_length=200)
    categoria = models.CharField(max_length=100)
    photo_url = models.URLField(default='https://picsum.photos/300/30', blank=True)
    video_url = models.URLField(blank=True, null=True)
    gallery_urls = ArrayField(
        models.URLField(max_length=500),
        blank=True,
        default=list
    )
    

    def __str__(self):
        return f"Nombre: {self.nombre}, Parroquia: {self.parroquia}"





########### USERS ###################


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given email, password and extra fields.
        """
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.is_active = False  # User is inactive by default
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Creates and saves a SuperUser with the given email, password and extra fields.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


######### SOCIAL COMPONENT ########

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.user.username} on {self.establecimiento.nombre}"

class CommentReply(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name_plural = 'Comment Replies'
    
    def __str__(self):
        return f"{self.user.username} replied to comment {self.comment.id}"

class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('comment', 'user')
    
    def __str__(self):
        return f"{self.user.username} likes comment {self.comment.id}"





class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'establecimiento')  # Ensure only one like per user and post

    def __str__(self):
        return f"{self.user.username} likes {self.establecimiento.nombre}"

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name='rating')
    rating = models.IntegerField(choices=((1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'establecimiento')  # Ensure only one rating per user and post

    def __str__(self):
        return f"{self.user.username} rated {self.establecimiento.nombre}: {self.rating}"
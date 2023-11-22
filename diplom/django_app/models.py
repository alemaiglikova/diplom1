from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models


class BusinessProject(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    likes = models.PositiveIntegerField(default=0)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    liked_by = models.ManyToManyField(User, related_name='liked_projects', blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(BusinessProject, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.project.title}'


class Review(models.Model):
    vacancy = models.ForeignKey('Vacancy', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comment = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return f'Review for {self.vacancy.vacancy}'


class Vacancy(models.Model):
    vacancy = models.CharField(max_length=100, default="Нет данных")
    full_name = models.CharField(max_length=100, default="Аноним")
    city = models.CharField(max_length=50, default="Не указан")
    experience = models.TextField(default="Опыт не указан")
    last_experience = models.TextField(default="Последний опыт не указан")
    about = models.TextField(default="Информация отсутствует")
    phone_number = models.CharField(max_length=15, default="Не указан")
    age = models.IntegerField(null=True, blank=True, default=0)
    face_photo = models.ImageField(upload_to='face_photos/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, default=3)
    reviews = models.ManyToManyField(Review, related_name='vacancies', blank=True)

    def __str__(self):
        return self.vacancy


class Work(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    requirements = models.TextField()
    contacts = models.CharField(max_length=100)
    publish_date = models.DateTimeField(default=timezone.now)
    published_by = models.ForeignKey(User, on_delete=models.CASCADE, default=3)
    responses = models.ManyToManyField(Vacancy, related_name='work_responses', blank=True)


class Room(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True)

    class Meta:
        ordering = ('name',)


class Message(models.Model):
    room = models.ForeignKey(Room, related_name="messages", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    content = models.TextField()
    date_added = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-date_added',)


class Product(models.Model):
    name = models.CharField(max_length=100, default='Название товара')
    description = models.TextField(default='Описание товара')
    category = models.CharField(max_length=100, default='Категория товара')
    image_url = models.URLField(default='https://example.com/default_image.jpg')

    def __str__(self):
        return self.name


import requests
from bs4 import BeautifulSoup
from django.contrib.auth.models import User

def get_leaderboard():
    # Получите список всех пользователей
    users = User.objects.all()

    # Создайте список, который будет содержать кортежи с количеством лайков и username
    leaderboard = [(user.liked_projects.count(), user.username) for user in users]

    # Отсортируйте список по убыванию количества лайков
    leaderboard.sort(reverse=True)

    # Верните 10 лидеров (если доступно)
    return leaderboard[:10]
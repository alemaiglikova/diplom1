from django.conf.urls.static import static
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.routers import DefaultRouter

from django_settings import settings
from . import views, views_a


schema_view = get_schema_view(
    openapi.Info(
        title="API каталога товаров",
        default_version='v1',
        description="RESTful API для получения информации о товарах, категориях и их характеристиках.",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="alem04kaa@mail.ru"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
)

urlpatterns = [
    path('', views.first_home, name='first_home'),
    path('home', views.home, name='home'),
    path('business_projects/', views.business_projects, name='business_projects'),
    path('business_projects/<int:pk>/', views.business_project_detail, name='business_project_detail'),
    path('business_projects/publish_idea', views.publish_idea, name='publish_idea'),
    path('business_projects/<int:pk>/delete/', views.delete_business_project, name='delete_business_project'),
    path('business_projects/<int:pk>/edit/', views.edit_business_project, name='edit_business_project'),

    path('like_project/<int:pk>/', views.like_project, name='like_project'),
    path('register/', views.register, name='register'),
    path('login', views.user_login, name='login'),
    path('delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('logout/', views.user_logout, name='logout'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('create_vacancy', views.create_vacancy, name='create_vacancy'),
    path('vacancy_list', views.vacancy_list, name='vacancy_list'),
    path('vacancy_detail/<int:pk>/', views.vacancy_detail, name='vacancy_detail'),
    path('add_review/<int:vacancy_id>/', views.add_review, name='add_review'),
    path('delete_vacancy/<int:pk>/', views.delete_vacancy, name='delete_vacancy'),
    path('edit_vacancy/<int:pk>/', views.edit_vacancy, name='edit_vacancy'),
    path('delete_review/<int:pk>/', views.delete_review, name='delete_review'),
    path('my_resume/', views.my_resume, name='my_resume'),

    path('create_work', views.create_work, name='create_work'),
    path('work_list', views.work_list, name='work_list'),
    path('work_detail/<int:pk>/', views.work_detail, name='work_detail'),
    path('delete_work/<int:pk>/', views.delete_work, name='delete_work'),
    path('edit_work/<int:pk>/', views.edit_work, name='edit_work'),
    path('submit_response/<int:work_id>/', views.submit_response, name='submit_response'),
    path('work_responses/<int:work_id>/', views.work_responses, name='work_responses'),
    # ...

    path('create_room/', views.create_room, name='create_room'),
    path('rooms/', views.rooms, name='rooms'),
    path('<slug:slug>/', views.room, name='room'),

    path('send_products_to_telegram', views.trigger_send_products_to_telegram, name='send_products_to_telegram'),





    path('api/communicate/', views.communicate, name='communicate'),
    path('api/products/', views.get_products, name='get_products'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # маршрут 1 api/communicat-будет вызывать функцию create

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
websocket_urlpatterns = [
    path('ws/<slug:room_name>/', views_a.ChatConsumer.as_asgi())
]

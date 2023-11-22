from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from django.core.mail import EmailMessage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import cache_page, never_cache
from django.views.decorators.http import require_POST

from rest_framework.decorators import api_view

import io
import requests
from reportlab.pdfgen import canvas
from celery import shared_task, canvas

import telebot
from django.shortcuts import redirect, get_object_or_404
from django_app.forms import CommentForm, BusinessIdeaForm, VacancyForm, WorkForm, ReviewForm
from django_app.models import BusinessProject, Comment, Vacancy, Review, Work, Product
from django_app.pars import get_leaderboard

from django.contrib.auth.models import User

from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from . import models
from .serializers import ProductSerializer


def first_home(request):
    """
    View for the first home page.

    Fetches data from an external API to get cryptocurrency prices and displays news headlines.

    Args:
        request: The HTTP request.

    Returns:
        Rendered HTML page with cryptocurrency prices and news headlines.
    """
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        bitcoin_price = data['bitcoin']['usd']
        ethereum_price = data['ethereum']['usd']
    else:
        bitcoin_price = None
        ethereum_price = None
        print("НЕТ ДАННЫХ")

    news_data = get_news()

    context = {
        'bitcoin_price': bitcoin_price,
        'ethereum_price': ethereum_price,
        'news_data': news_data
    }

    return render(request, 'first_home.html', context)


def register(request):
    """
    View for user registration.

    Handles user registration form submission, checks password validation and username uniqueness.

    Args:
        request: The HTTP request.

    Returns:
        Redirects to the login page on successful registration.
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # Password matching check
        if password != confirm_password:
            messages.error(request, 'Пароли не совпадают')
            return redirect('register')

        # Password length check
        if len(password) < 8:
            messages.error(request, 'Пароль слишком короткий (минимум 8 символов)')
            return redirect('register')

        # Unique username check
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует')
            return redirect('register')

        # Create user
        user = User.objects.create_user(username=username, password=password)
        user.save()
        print(f"User {user.username} has been created.")

        return redirect('login')

    return render(request, 'register.html')










def user_login(request):
    """
    View for user login.

    Handles user authentication and redirects to the home page on successful login.

    Args:
        request: The HTTP request.

    Returns:
        Redirects to the home page on successful login.
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            print(f"User {user.username} authenticated successfully.")
            return redirect('home')
        else:
            messages.error(request, 'Неверные учетные данные. Пожалуйста, попробуйте снова.')

    return render(request, 'login.html')


def user_logout(request):
    """
    View for user logout.

    Logs the user out and redirects to the login page.

    Args:
        request: The HTTP request.

    Returns:
        Redirects to the login page.
    """
    logout(request)
    return redirect('login')






















def get_news():
    """
    Fetches news data from an external API.

    Returns:
        List of news articles with titles, descriptions, and image URLs.
    """
    api_key = '7f0a348740a74186a2ac6f72db68c723'
    url = 'https://newsapi.org/v2/top-headlines'
    params = {
        'country': 'us',
        'apiKey': api_key
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        articles = data['articles']
        news_list = []

        for article in articles:
            title = article['title']
            description = article['description']
            image_url = article['urlToImage']

            news_list.append({'title': title, 'description': description, 'image_url': image_url})

        return news_list
    else:
        return None







@cache_page(60 * 5)
def home(request):
    """
    View for the home page.

    Fetches cryptocurrency prices and news data and displays them on the home page.

    Args:
        request: The HTTP request.

    Returns:
        Rendered HTML page with cryptocurrency prices and news data.
    """
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        bitcoin_price = data['bitcoin']['usd']
        ethereum_price = data['ethereum']['usd']
    else:
        bitcoin_price = None
        ethereum_price = None

    news_data = get_news()

    context = {
        'bitcoin_price': bitcoin_price,
        'ethereum_price': ethereum_price,
        'news_data': news_data
    }

    return render(request, 'home.html', context)



























@never_cache
def business_projects(request):
    """
    View for displaying a list of business projects.

    Fetches all business projects, orders them by the creation date, and paginates the results.

    Args:
        request: The HTTP request.

    Returns:
        Rendered HTML page with a paginated list of business projects.
    """
    projects = BusinessProject.objects.all().order_by('-created_at')

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(projects, 10)

    try:
        projects = paginator.page(page)
    except PageNotAnInteger:
        projects = paginator.page(1)
    except EmptyPage:
        projects = paginator.page(paginator.num_pages)

    liked_projects = BusinessProject.objects.filter(liked_by=request.user)
    context = {'projects': projects, 'liked_projects': liked_projects}
    return render(request, 'business_projects.html', context)


def business_project_detail(request, pk):
    """
    View for displaying details of a business project.

    Fetches the specified business project and its associated comments.

    Args:
        request: The HTTP request.
        pk: The primary key of the business project.

    Returns:
        Rendered HTML page with details of the business project and its comments.
    """
    project = get_object_or_404(BusinessProject, pk=pk)
    form = CommentForm()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                comment_text = form.cleaned_data['text']
                comment = Comment(user=request.user, project=project, text=comment_text)
                comment.save()
            else:
                return redirect('login')

    comments = project.comment_set.all()

    return render(request, 'business_project_detail.html', {'project': project, 'form': form, 'comments': comments})




@never_cache
def delete_business_project(request, pk):
    """
    View for deleting a business project.

    Deletes the specified business project if the user is an administrator or the owner.

    Args:
        request: The HTTP request.
        pk: The primary key of the business project.

    Returns:
        Redirects to the business projects page after deletion.
    """
    project = get_object_or_404(BusinessProject, pk=pk)

    if request.user.is_superuser or request.user == project.owner:
        project.delete()

    return redirect('business_projects')


@never_cache
def edit_business_project(request, pk):
    """
    View for editing a business project.

    Edits the specified business project if the user is an administrator or the owner.

    Args:
        request: The HTTP request.
        pk: The primary key of the business project.

    Returns:
        Renders a form for editing the business project or redirects to the business project details page.
    """
    project = get_object_or_404(BusinessProject, pk=pk)

    if request.user.is_superuser or request.user == project.owner:
        if request.method == 'POST':
            form = BusinessIdeaForm(request.POST, instance=project)
            if form.is_valid():
                form.save()
                print(f"Project {project.title} edited successfully.")
                return redirect('business_project_detail', pk=pk)
        else:
            form = BusinessIdeaForm(instance=project)

        return render(request, 'edit_business_project.html', {'form': form})
    else:
        return redirect('business_project_detail', pk=pk)


@never_cache
def publish_idea(request):
    """
    View for publishing a business idea.

    Handles the form submission for publishing a new business idea.

    Args:
        request: The HTTP request.

    Returns:
        Redirects to the business projects page after publishing the idea.
    """
    if request.method == 'POST':
        form = BusinessIdeaForm(request.POST)
        if form.is_valid():
            business_idea = form.save(commit=False)
            business_idea.owner = request.user
            business_idea.save()
            print(f"Название: {business_idea.title}, Описание: {business_idea.description}")
            return redirect('business_projects')
    else:
        form = BusinessIdeaForm()

    return render(request, 'publish_idea.html', {'form': form})


@require_POST
def like_project(request, pk):
    """
    View for liking/unliking a business project.

    Handles the AJAX request to like or unlike a business project.

    Args:
        request: The HTTP request.
        pk: The primary key of the business project.

    Returns:
        JSON response indicating whether the project was liked or unliked.
    """
    project = get_object_or_404(BusinessProject, pk=pk)
    liked = False

    if request.user.is_authenticated:
        if project.liked_by.filter(id=request.user.id).exists():
            project.liked_by.remove(request.user)
            project.likes = max(project.likes - 1, 0)
            liked = False
        else:
            project.liked_by.add(request.user)
            project.likes += 1
            liked = True

        project.save()

    return JsonResponse({'liked': liked})


@never_cache
def delete_comment(request: HttpRequest, comment_id: int) -> HttpResponse:
    """
    View for deleting a comment.

    Deletes the specified comment if the user is the owner.

    Args:
        request: The HTTP request.
        comment_id: The ID of the comment.

    Returns:
        Redirects to the business project details page after deletion.
    """
    comment = get_object_or_404(Comment, id=comment_id)
    project_id = comment.project.id

    if request.user == comment.user:
        comment.delete()

    return redirect('business_project_detail', pk=project_id)


def leaderboard(request):
    """
    View for displaying a leaderboard.

    Fetches the leaderboard data and renders the leaderboard page.

    Args:
        request: The HTTP request.

    Returns:
        Rendered HTML page with the leaderboard data.
    """
    leaderboard = get_leaderboard()
    return render(request, 'leaderboard.html', {'leaderboard': leaderboard})



















def create_vacancy(request):
    """
    View for creating a new vacancy.

    Handles the form submission for creating a new vacancy.

    Args:
        request: The HTTP request.

    Returns:
        Redirects to the vacancy list page after creating the vacancy.
    """
    if request.method == 'POST':
        form = VacancyForm(request.POST, request.FILES)
        if form.is_valid():
            # Extract form data
            vacancy = form.cleaned_data.get('vacancy')
            full_name = form.cleaned_data.get('full_name')
            age = form.cleaned_data.get('age')
            city = form.cleaned_data.get('city')
            experience = form.cleaned_data.get('experience')
            last_experience = form.cleaned_data.get('last_experience')
            about = form.cleaned_data.get('about')
            phone_number = form.cleaned_data.get('phone_number')
            face_photo = request.FILES.get('face_photo')

            # Create and save the new vacancy
            new_vacancy = Vacancy(
                vacancy=vacancy,
                full_name=full_name,
                age=age,
                city=city,
                experience=experience,
                last_experience=last_experience,
                about=about,
                phone_number=phone_number,
                face_photo=face_photo
            )

            new_vacancy.save()
            print("Вакансия успешно сохранена в базе данных.")

            return redirect('vacancy_list')
        else:
            print("Валидация не прошла")
            print(form.errors)
    else:
        form = VacancyForm()

    return render(request, 'create_vacancy.html', {'form': form})


def vacancy_list(request):
    """
    View for displaying a list of vacancies.

    Fetches the vacancies, applies search filtering, orders them by creation date, and paginates the results.

    Args:
        request: The HTTP request.

    Returns:
        Rendered HTML page with a paginated list of vacancies.
    """
    search_query = request.GET.get('search', '')

    if search_query:
        vacancies = Vacancy.objects.filter(
            Q(vacancy__icontains=search_query) |
            Q(full_name__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(last_experience__icontains=search_query)
        )
    else:
        vacancies = Vacancy.objects.all()

    vacancies = vacancies.order_by('-created_at')

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(vacancies, 10)
    try:
        vacancies = paginator.page(page)
    except PageNotAnInteger:
        vacancies = paginator.page(1)
    except EmptyPage:
        vacancies = paginator.page(paginator.num_pages)

    context = {'vacancies': vacancies}
    return render(request, 'vacancy_list.html', context)


def vacancy_detail(request, pk):
    """
    View for displaying details of a vacancy.

    Fetches the specified vacancy, its associated reviews, and renders the details page.

    Args:
        request: The HTTP request.
        pk: The primary key of the vacancy.

    Returns:
        Rendered HTML page with details of the vacancy and its reviews.
    """
    vacancy = get_object_or_404(Vacancy, pk=pk)
    reviews = Review.objects.filter(vacancy=vacancy)

    total_rating = sum([review.rating for review in reviews])
    average_rating = total_rating / len(reviews) if reviews else 0

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.vacancy = vacancy
            review.save()
            return redirect('vacancy_detail', pk=pk)
    else:
        form = ReviewForm()

    context = {
        'vacancy': vacancy,
        'reviews': reviews,
        'average_rating': average_rating,
        'form': form,
    }

    return render(request, 'vacancy_detail.html', context)


@never_cache
def add_review(request, vacancy_id):
    """
    View for adding a review to a vacancy.

    Handles the form submission for adding a new review to a vacancy.

    Args:
        request: The HTTP request.
        vacancy_id: The ID of the vacancy to which the review is added.

    Returns:
        Redirects to the vacancy details page after adding the review.
    """
    vacancy = get_object_or_404(Vacancy, pk=vacancy_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.vacancy = vacancy
            review.author = request.user
            review.save()
            return redirect('vacancy_detail', pk=vacancy_id)
    else:
        form = ReviewForm()

    return render(request, 'vacancy_detail.html', {'form': form, 'vacancy': vacancy})


@never_cache
def delete_review(request, pk):
    """
    View for deleting a review.

    Deletes the specified review if the user is the owner or a superuser.

    Args:
        request: The HTTP request.
        pk: The ID of the review.

    Returns:
        Redirects to the vacancy details page after deletion.
    """
    review = get_object_or_404(Review, pk=pk)

    if request.user.is_authenticated and (request.user.is_superuser or request.user == review.author):
        review.delete()
        return redirect('vacancy_detail', pk=review.vacancy.pk)
    else:
        return HttpResponseForbidden()


@never_cache
def delete_vacancy(request, pk):
    """
    View for deleting a vacancy.

    Deletes the specified vacancy if the user is the owner or a superuser.

    Args:
        request: The HTTP request.
        pk: The ID of the vacancy.

    Returns:
        Redirects to the vacancy list page after deletion.
    """
    vacancy = get_object_or_404(Vacancy, pk=pk)

    if request.user.is_authenticated and (request.user.is_superuser or request.user == vacancy.created_by):
        vacancy.delete()
        return redirect('vacancy_list')
    else:
        return HttpResponseForbidden()


def edit_vacancy(request, pk):
    """
    View for editing a vacancy.

    Edits the specified vacancy if the user is the owner or a superuser.

    Args:
        request: The HTTP request.
        pk: The ID of the vacancy.

    Returns:
        Renders a form for editing the vacancy.
    """
    vacancy = get_object_or_404(Vacancy, pk=pk)

    if request.user.is_authenticated and (request.user.is_superuser or request.user == vacancy.created_by):
        if request.method == 'POST':
            form = VacancyForm(request.POST, request.FILES, instance=vacancy)
            if form.is_valid():
                form.save()
                return redirect('vacancy_detail', pk=pk)
        else:
            form = VacancyForm(instance=vacancy)

        context = {
            'form': form,
            'vacancy': vacancy
        }

        return render(request, 'edit_vacancy.html', context)
    else:
        return HttpResponseForbidden()


@login_required
def my_resume(request):
    """
    View for displaying the user's resumes.

    Fetches the resumes created by the current user and renders the 'my_resume' page.

    Args:
        request: The HTTP request.

    Returns:
        Rendered HTML page with the user's resumes.
    """
    user = request.user
    vacancies = Vacancy.objects.filter(created_by=user)

    context = {'vacancies': vacancies}
    return render(request, 'my_resume.html', context)


















@never_cache
def create_work(request):
    """
    View for creating a work.

    Handles the form submission for creating a new work.

    Args:
        request: The HTTP request.

    Returns:
        Redirects to the work list page after creating the work.
    """
    if request.method == 'POST':
        form = WorkForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('work_list')
    else:
        form = WorkForm()
    return render(request, 'create_work.html', {'form': form})


@never_cache
def work_list(request):
    """
    View for displaying a list of works.

    Fetches the works, applies search filtering, orders them by publish date, and paginates the results.

    Args:
        request: The HTTP request.

    Returns:
        Rendered HTML page with a paginated list of works.
    """
    search_query = request.GET.get('search', '')

    if search_query:
        works = Work.objects.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(requirements__icontains=search_query) |
            Q(contacts__icontains=search_query) |
            Q(published_by__icontains=search_query)
        )
    else:
        works = Work.objects.all()
    works = works.order_by('-publish_date')

    page = request.GET.get('page', 1)
    paginator = Paginator(works, 10)
    try:
        works = paginator.page(page)
    except PageNotAnInteger:
        works = paginator.page(1)
    except EmptyPage:
        works = paginator.page(paginator.num_pages)

    context = {'works': works}
    return render(request, 'work_list.html', context)


def work_detail(request, pk):
    """
    View for displaying details of a work.

    Fetches the details of the specified work and renders the 'work_detail' page.

    Args:
        request: The HTTP request.
        pk: The ID of the work.

    Returns:
        Rendered HTML page with the details of the work.
    """
    work = get_object_or_404(Work, pk=pk)

    context = {'work': work}

    return render(request, 'work_detail.html', context)


@never_cache
def delete_work(request, pk):
    """
    View for deleting a work.

    Deletes the specified work if the user is the owner or a superuser.

    Args:
        request: The HTTP request.
        pk: The ID of the work.

    Returns:
        Redirects to the work list page after deletion.
    """
    work = get_object_or_404(Work, pk=pk)

    if request.user.is_authenticated and (request.user.is_superuser or request.user == work.published_by):
        work.delete()
        return redirect('work_list')  # Redirect to the work list page after deletion
    else:
        return redirect('work_detail', pk=pk)


def edit_work(request, pk):
    """
    View for editing a work.

    Edits the specified work if the user is the owner or a superuser.

    Args:
        request: The HTTP request.
        pk: The ID of the work.

    Returns:
        Renders a form for editing the work.
    """
    work = get_object_or_404(Work, pk=pk)

    if request.user.is_authenticated and (request.user.is_superuser or request.user == work.published_by):
        if request.method == 'POST':
            form = WorkForm(request.POST, instance=work)
            if form.is_valid():
                form.save()
                return redirect('work_detail', pk=pk)
        else:
            form = WorkForm(instance=work)

        context = {'form': form, 'work': work}
        return render(request, 'edit_work.html', context)
    else:
        return redirect('work_detail', pk=pk)


















def submit_response(request, work_id):
    """
    View for submitting a response to a work.

    Handles the submission of a response to a work by connecting it to a vacancy.

    Args:
        request: The HTTP request.
        work_id: The ID of the work.

    Returns:
        HttpResponse with a success message.
    """
    if request.method == 'POST':
        vacancy_id = request.POST.get('vacancy')
        work = get_object_or_404(Work, pk=work_id)
        vacancy = get_object_or_404(Vacancy, pk=vacancy_id)
        work.responses.add(vacancy)
        work.save()
        return HttpResponse('Отклик успешно отправлен!')
    elif request.method == 'GET':
        user_vacancies = Vacancy.objects.filter(created_by=request.user)
        work = get_object_or_404(Work, pk=work_id)
        context = {'work': work, 'user_vacancies': user_vacancies}
        print(user_vacancies)  # Print resumes to the console for debugging
        return render(request, 'submit_response.html', context)




def work_responses(request, work_id):
    """
    View for displaying responses to a work.

    Fetches the responses to the specified work and renders the 'work_responses' page.

    Args:
        request: The HTTP request.
        work_id: The ID of the work.

    Returns:
        Rendered HTML page with the responses to the work.
    """
    work = get_object_or_404(Work, pk=work_id)
    context = {'work': work}
    return render(request, 'work_responses.html', context)









@shared_task
def send_weekly_product_list(recipient_email):
    """
    Celery task for sending a weekly product list as a PDF attachment to the specified email.

    Args:
        recipient_email: The email address of the recipient.

    Returns:
        None
    """
    try:
        # Retrieve the list of products
        products = Product.objects.values_list('name', flat=True)

        # Create a PDF file
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 750, "Еженедельный список товаров:")

        y = 700
        for product in products:
            y -= 20
            p.drawString(100, y, product)

        p.showPage()
        p.save()

        pdf = buffer.getvalue()
        buffer.close()

        # Send the PDF file by email
        subject = "Еженедельный список товаров"
        body = "Во вложении находится ваш список товаров."

        email_message = EmailMessage(subject, body, "'alem04kaa@mail.ru'", [recipient_email])
        email_message.attach('product_list.pdf', pdf, 'application/pdf')
        email_message.send()
    except Exception as e:
        print("Error sending email:", e)












def communicate(request):
    """
    View for fetching data from an external source and saving it to the database.

    Fetches data from the external source 'https://fakestoreapi.com/products' and saves it to the 'Product' model.

    Args:
        request: The HTTP request.

    Returns:
        HttpResponse with a success or error message.
    """
    try:
        response = requests.get('https://fakestoreapi.com/products')
        response.raise_for_status()
        data = response.json()
        print("Received data from external source:", data)  # Debugging message

        for item in data:
            product = Product(
                name=item['title'],
                description=item['description'],
                category=item['category'],
                image_url=item['image']
            )
            product.save()
            email_to = "iglikovaalema406@gmail.com"
            send_weekly_product_list.apply_async(args=[email_to])

        return HttpResponse("Data successfully received and saved to the database.", status=200)

    except requests.exceptions.HTTPError as errh:
        print("HTTP Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Something went wrong:", err)

    return HttpResponse("An error occurred while fetching data from the external source.", status=500)


@api_view(['GET'])
def get_products(request):
    """
    API view for retrieving a list of products.

    Retrieves a list of products based on the optional 'search' query parameter.

    Args:
        request: The HTTP request.

    Returns:
        Rendered HTML page with the list of products.
    """
    queryset = Product.objects.all()

    search_query = request.query_params.get('search', '')
    if search_query:
        queryset = queryset.filter(name__icontains=search_query)

    serializer = ProductSerializer(queryset, many=True)
    context = {
        'products': serializer.data
    }
    return render(request, 'product_list.html', context)


def send_products_to_telegram(request):
    """
    View for sending products to a Telegram user.

    Sends a message to a Telegram user with the list of products obtained from an external source.

    Args:
        request: The HTTP request.

    Returns:
        HttpResponse with a success or error message.
    """
    try:
        def send_telegram_message(message_text):
            bot = telebot.TeleBot('6416365019:AAEM1tvgcXngl1yH0nWfKMzusSRpg3-K9r4')
            bot.send_message(1077739312, message_text)  # Replace with your user ID

        # Retrieve product list
        response = requests.get('https://fakestoreapi.com/products')
        response.raise_for_status()
        data = response.json()
        print("Received data from external source:", data)  # Debugging message

        # Prepare message text
        message_text = "Список товаров:\n"
        for item in data:
            item_text = f"Название: {item['title']}\nОписание: {item['description']}\nКатегория: {item['category']}\n\n"
            if len(message_text) + len(item_text) <= 4000:
                message_text += item_text
            else:
                break

        # Send message to Telegram
        send_telegram_message(message_text)

        return HttpResponse("Products sent to Telegram successfully!")

    except requests.exceptions.RequestException as err:
        return HttpResponse(f"Something went wrong: {err}")


def trigger_send_products_to_telegram(request):
    """
    View for triggering the sending of products to Telegram.

    Calls the main function to send products to Telegram.

    Args:
        request: The HTTP request.

    Returns:
        HttpResponse with a success message.
    """
    # Call the main function to send products to Telegram
    return send_products_to_telegram(request)












@login_required
def create_room(request):
    """
    View for handling the creation of a new room.

    Requires the user to be authenticated.

    Parameters:
    - request: HttpRequest object

    Returns:
    - If the request method is POST:
        - Creates a new room with the provided name, slug, and assigns the current user as the owner.
        - Redirects to the 'rooms' page.
    - If the request method is not POST:
        - Renders the 'create_room.html' template.

    Template:
    - 'create_room.html'
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        user = request.user
        room = models.Room.objects.create(name=name, slug=slug, owner=user)
        return redirect('rooms')

    return render(request, 'create_room.html')


def rooms(request):
    """
    View for displaying a list of all rooms.

    Parameters:
    - request: HttpRequest object

    Returns:
    - Renders the 'house.html' template with a context containing all rooms.

    Template:
    - 'house.html'
    """
    return render(request, "house.html", context={"rooms": models.Room.objects.all()})


@login_required
def room(request, slug):
    """
    View for displaying details of a specific room.

    Requires the user to be authenticated.

    Parameters:
    - request: HttpRequest object
    - slug: The unique identifier for the room

    Returns:
    - If the room with the provided slug is found:
        - Prints a debug message with the requested slug.
        - Retrieves the room and the latest two messages associated with it.
        - Renders the 'room.html' template with the room and messages in the context.
    - If the room with the provided slug is not found:
        - Returns a 404 response.

    Template:
    - 'room.html'
    """
    print(f"Requested slug: {slug}")
    room_obj = get_object_or_404(models.Room, slug=slug)
    messages = models.Message.objects.filter(room=room_obj)[:2][::-1]
    print(f"Room found: {room_obj.name}")
    return render(
        request,
        "room.html",
        context={"room": room_obj, "messages": messages}
    )



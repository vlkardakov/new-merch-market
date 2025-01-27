from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.html import escape
from .models import Product, Review
import telebot
import os
from django.db.models import Q
from django.contrib.auth.decorators import login_required


BOT_TOKEN = "7508512512:AAHOuu8klbbKR6AL-5Q4qgD_bBmHHLPZLNI"
CHAT_ID = "6901083609"

bot = telebot.TeleBot(BOT_TOKEN)

# Create your views here.

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserCreationForm, LoginForm

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                form.add_error(None, "Invalid credentials")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')


def home(request):
    search = request.GET.get('search')

    if search:
        products = Product.objects.filter(Q(name__contains=search) | Q(description__contains=search))
    else:
        products = Product.objects.all()

    return render(request, 'index.html', {'products': products, 'search': escape(search) if search else ''})

def view_product(request, id):
    product = Product.objects.filter(id=id).first()

    if request.method == "POST":
        author = request.POST.get('author')
        rating = request.POST.get('rating')
        usage_duration = request.POST.get('duration')
        text = request.POST.get('review')

        review = Review(
            product=product,
            author=author,
            rating=rating,
            usage_duration=usage_duration,
            text=text,
        )
        review.save()

    reviews = product.review_set.all()

    return render(request, 'product.html', {
        'product': product,
        'reviews': reviews,
    })

from django.shortcuts import render, redirect
from django_telegram_login.widgets.constants import (
    SMALL, MEDIUM, LARGE
)
from django_telegram_login.widgets.generator import (
    create_callback_login_widget
)
from django_telegram_login.authentication import verify_telegram_authentication

def telegram_login(request):
    telegram_login_widget = create_callback_login_widget(
        bot_name='Мерч Маркет',
        size=MEDIUM,
        user_photo=True
    )
    return render(request, 'telegram_login.html', {'telegram_login_widget': telegram_login_widget})

def telegram_callback(request):
    result = verify_telegram_authentication(bot_token='7316556593:AAE0UAuEkVc_anc08EN16AxR_OdcTZ5C67I', request_data=request.GET)
    if result:
        from django.contrib.auth import login
        from .models import CustomUser

        def telegram_callback(request):
            result = verify_telegram_authentication(bot_token='7316556593:AAE0UAuEkVc_anc08EN16AxR_OdcTZ5C67I   ', request_data=request.GET)
            if result:
                telegram_id = result['id']
                user, created = CustomUser.objects.get_or_create(telegram_id=telegram_id)
                login(request, user)
                return redirect('/')
            else:
                return redirect('login')

        return redirect('/')
    else:
        return redirect('login')


def payment(request, id):
    product = Product.objects.filter(id=id).first()
    try:
        if request.method == "POST":
            user = request.user
            address = request.POST.get('address')
            communication = request.POST.get('phone')

            if user.balance >= product.price:
                user.balance -= product.price
                user.save()

                about_customer = f"""
юзернейм: {user.username}
Электронная почта: {user.email}
Дата регистрации: {user.date_joined}
Текущий баланс: {user.balance}
            """

                bot.send_message(CHAT_ID, f'''Новый заказ: {product.name}
Цена: {product.price} баллов
Заказчик: {about_customer}

Адрес: {address}

Способ связи: {communication}

''')
                return redirect('/success')
            else:
                return render(request, 'payment_failed.html', {'product': product})

        return render(request, "payment.html", {
            'product': product
        })
    except:
        return redirect('/login')

from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm
import telegram

from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseForbidden


@staff_member_required
def approve_user(request, username):
    if not request.user.is_superuser:
        return HttpResponseForbidden("У вас нет прав для выполнения этой операции.")

    user_to_approve = get_object_or_404(User, username=username)
    user_to_approve.is_active = True
    user_to_approve.save()

    return redirect('/success')  # Перенаправление на страницу успешного завершения


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            
            admin_chat_id = '6901083609'
            message = f"Подтвердите регистрацию:\nюзернейм: {user.username}"
            bot.send_message(chat_id=admin_chat_id, text=message)

            return redirect('waiting_approval')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def waiting_approval(request):
    return render(request, 'waiting_approval.html')


def success(request):
    return render(request, 'success.html')

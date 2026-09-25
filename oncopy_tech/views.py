from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
import requests
import json
from .models import RepairRequest


def get_client_ip(request):
    """Получение IP-адреса пользователя (с учётом прокси)"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def check_captcha(token, request):
    """Проверка токена Yandex SmartCaptcha на сервере"""
    url = "https://captcha-api.yandex.ru/validate"
    params = {
        "secret": settings.YANDEX_CAPTCHA_SERVER_KEY,
        "token": token,
        "ip": get_client_ip(request),
    }
    try:
        # Используем POST для безопасности (как рекомендует Yandex)
        response = requests.post(url, data=params, timeout=5)
        if response.status_code != 200:
            print(f"Captcha error: code={response.status_code}, body={response.text}")
            return False
        result = response.json()
        return result.get("status") == "ok"
    except requests.RequestException as e:
        print(f"Captcha connection error: {e}")
        return False


def send_repair_email(phone):
    """Отправка заявки на почту"""
    subject = "🔧 Новая заявка на ремонт принтера"
    message = (
        f"Новая заявка с сайта Oncopy-tech\n\n"
        f"📱 Телефон: {phone}\n"
    )
    recipient_list = ['sale@oncopy.ru', 'rykinegor@yandex.ru']

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        print(f"✅ Письмо отправлено на {recipient_list}")
        return True
    except Exception as e:
        print(f"❌ Ошибка отправки письма: {e}")
        return False


def index(request):
    return render(request, 'oncopy_tech/index.html')


@csrf_exempt
def submit_request(request):
    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        captcha_token = request.POST.get('smart-token', '')

        # 1. Проверка номера телефона
        if not phone or len(phone) < 10:
            return JsonResponse({
                'success': False,
                'error': 'Введите корректный номер телефона'
            })

        # 2. Проверка капчи
        if not captcha_token:
            return JsonResponse({
                'success': False,
                'error': 'Пройдите проверку капчи'
            })

        if not check_captcha(captcha_token, request):
            return JsonResponse({
                'success': False,
                'error': 'Капча не пройдена. Попробуйте снова.'
            })

        # 3. Сохраняем заявку в БД
        RepairRequest.objects.create(phone=phone)

        # 4. Отправляем на почту
        send_repair_email(phone)

        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Неверный метод'})
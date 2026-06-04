from django.contrib.auth import get_user_model
from django.db import transaction
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, TemplateView, ListView, View
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordResetView,
)
from django.contrib import messages
from django.http import JsonResponse
from phonenumber_field.phonenumber import PhoneNumber
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth.tokens import default_token_generator
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from datetime import timedelta

from phonenumbers import NumberParseException

from users.models import Notification

from config.settings import FIREBASE_API_KEY
from users.forms import CustomAuthenticationForm, CustomUserCreationForm
from users.utils import send_custom_email

User = get_user_model()


class RegisterView(CreateView):
    template_name = "users/pages/register.html"
    form_class = CustomUserCreationForm

    def form_valid(self, form):
        # Оборачиваем в транзакцию: письмо уйдет только если юзер реально создался
        with transaction.atomic():
            # Сохраняем пользователя как неактивного
            user = form.save(commit=False)
            user.email_confirmed = False
            user.save()

        # Отправляем письмо активации
        self.send_activation_email(user)

        messages.success(
            self.request,
            "Регистрация прошла успешно! Проверьте почту для активации аккаунта.",
        )
        # Используем явный редирект, чтобы избежать повторного form.save() в super().form_valid(form)
        # второй save() менял пользователя и делал token недействительным
        return redirect("users:login")

    def send_activation_email(self, user):
        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))
        activation_url = self.request.build_absolute_uri(
            reverse_lazy(
                "users:activate_account", kwargs={"uidb64": uidb64, "token": token}
            )
        )

        send_custom_email(
            subject="Активация аккаунта",
            template_name="users/emails/activation.html",
            context={"user": user, "activation_url": activation_url},
            to_email=user.email,
            request=self.request,
        )


def activate_account_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.email_confirmed = True
        user.save()
        messages.success(
            request, "Аккаунт успешно активирован! Теперь Вы можете войти."
        )
        return redirect("users:login")
    else:
        messages.error(request, "Ссылка активации недействительна или устарела!")
        return redirect("users:registration")


class CustomLoginView(LoginView):
    template_name = "users/pages/login.html"
    authentication_form = CustomAuthenticationForm

    def get_success_url(self):
        next_url = self.request.GET.get("next")
        if next_url:
            return next_url
        return reverse("users:profile", kwargs={"username": self.request.user.username})


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("ads:ad_list")


@require_POST
@login_required
def set_phone_number(request):
    phone_raw = request.POST.get("phone_number")
    user = request.user

    try:
        parsed_phone = PhoneNumber.from_string(phone_raw, region="RU")
        if not parsed_phone.is_valid():
            raise ValueError("Invalid number")

        if user.phone_number == parsed_phone:
            messages.info(request, "Этот номер уже привязан.")
            return redirect("users:settings")

        # Проверка на дубликаты у других подтвержденных юзеров
        if User.objects.filter(
            phone_number=parsed_phone, phone_number_verified=True
        ).exists():
            messages.warning(request, "Номер уже занят другим пользователем.")
            return redirect("users:settings")

        # Сохраняем
        user.phone_number = parsed_phone
        user.phone_number_verified = False
        user.save()
        messages.success(request, "Номер телефона обновлен.")

    except (NumberParseException, ValueError):
        messages.warning(request, "Некорректный формат номера телефона.")

    return redirect("users:settings")


@require_POST
@login_required
def mark_phone_number_as_verified(request):
    user = request.user
    user.phone_number_verified = True
    user.save(update_fields=["phone_number_verified"])

    # ОПТИМИЗАЦИЯ: удаляем этот номер у всех остальных одним запросом
    User.objects.filter(phone_number=user.phone_number).exclude(id=user.id).update(
        phone_number=None, phone_number_verified=False
    )

    return JsonResponse({"success": True})


class CustomPasswordChangeView(PasswordChangeView):
    template_name = "users/pages/password_change.html"
    success_url = reverse_lazy("users:password_change_done")

    def form_valid(self, form):
        messages.success(self.request, "Пароль успешно изменен!")
        return super().form_valid(form)


class PasswordChangeDoneView(TemplateView):
    template_name = "users/pages/password_change_done.html"


class ProfilePasswordResetView(PasswordResetView):
    template_name = "users/pages/password_reset_profile.html"
    email_template_name = ("users/emails/password_reset.txt",)
    html_email_template_name = ("users/emails/password_reset.html",)
    subject_template_name = "users/emails/subjects/password_reset.txt"
    success_url = reverse_lazy("users:profile_password_reset_instructions_sent")

    def post(self, request, *args, **kwargs):
        request.POST = request.POST.copy()
        request.POST["email"] = request.user.email

        messages.success(request, f"Письмо отправлено на {request.user.email}")

        return super().post(request, *args, **kwargs)


@require_POST
def toggle_theme(request):
    """Смена темы (база для юзеров, сессия для гостей)"""
    if request.user.is_authenticated:
        new_theme = "light" if request.user.selected_theme == "dark" else "dark"
        request.user.selected_theme = new_theme
        # update_fields критически важен для производительности моделей с кучей полей
        request.user.save(update_fields=["selected_theme"])
    else:
        new_theme = (
            "light" if request.session.get("theme", "dark") == "dark" else "dark"
        )
        request.session["theme"] = new_theme

    return JsonResponse({"new_theme": new_theme})


class SettingsView(TemplateView):
    """Страница настроек профиля"""

    template_name = "users/pages/settings.html"
    extra_context = {
        "FIREBASE_API_KEY": FIREBASE_API_KEY,
    }


class ProfileView(DetailView):
    model = User
    slug_url_kwarg = "username"
    slug_field = "username"
    template_name = "users/pages/index.html"
    context_object_name = "profile_user"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = self.object
        is_owner = self.request.user == profile_user

        #  Работа с объявлениями
        ads_qs = profile_user.ads.all().order_by("-created_at")
        if not is_owner:
            ads_qs = ads_qs.filter(status="published")

        # Контекст для BatchLoader
        context.update(
            {
                "ads": ads_qs[:3],
                "has_more_ads": ads_qs.count() > 3,
                "ads_per_batch": 3,
                "owner_id": profile_user.id,
                "show_all": is_owner,
                "is_owner": is_owner,
            }
        )

        # НОВЫЙ РЕЙТИНГ (Звезды)
        # Берем готовые данные (avg, full, half, empty) из модели User
        context["rating"] = profile_user.rating_data

        # Оценка текущего пользователя
        if self.request.user.is_authenticated:
            user_rating = profile_user.received_ratings.filter(
                voter=self.request.user
            ).first()
            # Передаем оценку (число 1-5), которую поставил залогиненный юзер, или 0
            context["user_current_score"] = user_rating.score if user_rating else 0

        return context


# полностью запрещаем браузеру и промежуточным серверам кэшировать эту страницу
@method_decorator(never_cache, name="dispatch")
class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = "users/pages/notifications.html"
    context_object_name = "notifications"

    def get_queryset(self):
        # Удаляем всё, что старше 30 дней
        self.request.user.notifications.filter(
            created_at__lt=timezone.now() - timedelta(days=30)
        ).delete()
        return self.request.user.notifications.all()

    def post(self, request, *args, **kwargs):
        if "mark_all_read" in request.POST:
            request.user.notifications.filter(is_read=False).update(is_read=True)
        elif "delete_all" in request.POST:
            request.user.notifications.all().delete()
        return redirect("users:notifications")


@login_required
@require_POST
def toggle_notifications(request):
    user = request.user
    # Переключаем флаг
    user.notifications_enabled = not user.notifications_enabled
    user.save(update_fields=["notifications_enabled"])
    return JsonResponse({"notifications_enabled": user.notifications_enabled})


@login_required
def read_and_redirect(request, notification_id):
    # Ищем уведомление, принадлежащее именно этому пользователю
    notification = get_object_or_404(
        Notification, id=notification_id, recipient=request.user
    )

    # Помечаем как прочитанное
    if not notification.is_read:
        notification.is_read = True
        notification.save(update_fields=["is_read"])

    # Перенаправляем на страницу объявления
    if notification.content_object:
        # Проверяем, есть ли у объявления slug
        if hasattr(notification.content_object, "slug"):
            return redirect("ads:ad_details", ad_slug=notification.content_object.slug)
        elif hasattr(notification.content_object, "get_absolute_url"):
            return redirect(notification.content_object.get_absolute_url())

    # Если объявления нет (удалено), возвращаем в список уведомлений
    return redirect("users:notifications")


class NotificationListViewJSON(LoginRequiredMixin, View):
    """Получение списка уведомлений (JSON)"""

    def get(self, request):
        notifications = (
            Notification.objects.filter(recipient=request.user)
            .select_related("sender")
            .order_by("-created_at")[:5]
        )

        notifications_data = []
        for notification in notifications:
            notifications_data.append(
                {
                    "id": notification.id,
                    "sender": (
                        notification.sender.username
                        if notification.sender
                        else "Система"
                    ),
                    "type": notification.get_notification_type_display(),
                    "message": notification.message,
                    "is_read": notification.is_read,
                    "created_at": timezone.localtime(notification.created_at).strftime(
                        "%d.%m.%Y %H:%M"
                    ),
                }
            )

        return JsonResponse({"notifications": notifications_data})


class MarkNotificationReadView(LoginRequiredMixin, View):
    """Отметить одно уведомление как прочитанное"""

    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.is_read = True
        notification.save()

        unread_count = request.user.notifications.filter(is_read=False).count()

        return JsonResponse({"status": "ok", "unread_count": unread_count})


class MarkAllNotificationsReadView(LoginRequiredMixin, View):
    """Отметить все уведомления как прочитанные"""

    def post(self, request):
        Notification.objects.filter(recipient=request.user, is_read=False).update(
            is_read=True
        )

        return JsonResponse({"status": "ok", "unread_count": 0})


class UnreadNotificationsCountView(LoginRequiredMixin, View):
    """Получить количество непрочитанных уведомлений"""

    def get(self, request):
        count = request.user.notifications.filter(is_read=False).count()
        return JsonResponse({"unread_count": count})


class DeleteNotificationView(LoginRequiredMixin, View):
    """Удаление одного уведомления"""

    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.delete()
        return JsonResponse({"status": "ok"})


class DeleteAllNotificationsView(LoginRequiredMixin, View):
    """Удаление всех уведомлений пользователя"""

    def post(self, request):
        request.user.notifications.all().delete()
        return JsonResponse({"status": "ok"})

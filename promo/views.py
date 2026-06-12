import sys

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import FormView, View, ListView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Prefetch, Count, Q

from .forms import PaidServiceRequestForm, PaidServiceReviewForm, PaymentOrderForm
from .models import Type, Review, Service, Purchase, PaymentOrder
from .services import YooKassaPaymentService
from ads.models import Advertisement


class CreateRequestView(LoginRequiredMixin, View):
    def get(self, request, service_id):
        service = get_object_or_404(Service, id=service_id)
        form = PaidServiceRequestForm()
        form.fields["ad"].queryset = Advertisement.objects.filter(owner=request.user)

        # Предзаполняем выпадающие списки значениями по умолчанию, чтобы юзеру не нужно было кликать
        form.fields["service"].initial = service.id
        form.fields["type"].initial = (
            service.types.first().id if service.types.exists() else None
        )

        if hasattr(request.user, "phone_number") and request.user.phone_number:
            form.fields["phone"].initial = request.user.phone_number

        return render(
            request,
            "promo/request_form.html",
            {"form": form, "service": service},
        )

    def post(self, request, service_id):
        service = get_object_or_404(Service, id=service_id)
        form = PaidServiceRequestForm(request.POST)
        form.fields["ad"].queryset = Advertisement.objects.filter(owner=request.user)

        if form.is_valid():
            request_obj = form.save(commit=False)
            request_obj.user = request.user
            request_obj.save()
            return render(request, "promo/request_thanks.html")

        return render(
            request,
            "promo/request_form.html",
            {"form": form, "service": service},
        )


class CreateReviewView(LoginRequiredMixin, View):
    """Оставить отзыв на услугу продвижения"""

    def get(self, request, service_id):
        service = get_object_or_404(Service, id=service_id)
        form = PaidServiceReviewForm()
        return render(
            request, "promo/review_form.html", {"form": form, "service": service}
        )

    def post(self, request, service_id):
        service = get_object_or_404(Service, id=service_id)
        form = PaidServiceReviewForm(request.POST)

        # Проверяем строго по author_id, чтобы запрос 100% совпал с индексом базы данных PostgreSQL!
        if Review.objects.filter(
            author_id=request.user.id, service_id=service.id
        ).exists():
            return render(
                request,
                "promo/review_form.html",
                {
                    "form": form,
                    "service": service,
                    # Передаем текст ошибки, который отобразится на странице формы
                    "error_message": "Вы уже оставили отзыв на эту услугу. Второй раз этого сделать нельзя.",
                },
            )

        if form.is_valid():
            review = form.save(commit=False)
            review.author = request.user
            review.service = service
            review.save()
            return render(request, "promo/review_thanks.html")

        return render(
            request, "promo/review_form.html", {"form": form, "service": service}
        )


class ServiceListView(View):
    """Каталог тарифов и пакетов услуг продвижения"""

    def get(self, request):
        # Извлекаем типы услуг и предварительно загружаем связанные услуги и опубликованные отзывы
        types = Type.objects.prefetch_related(
            Prefetch(
                "services",
                queryset=Service.objects.prefetch_related("reviews").annotate(
                    average_rating=Avg(
                        "reviews__rating", filter=Q(reviews__status="published")
                    ),
                    reviews_count=Count(
                        "reviews", filter=Q(reviews__status="published")
                    ),
                ),
            )
        ).all()

        # Расчет процентов для точной отрисовки звезд на CSS-масках
        for t in types:
            for service in t.services.all():
                if service.average_rating:
                    # Превращаем рейтинг (например 4.3) в проценты для CSS (86%)
                    service.average_rating_percent = (service.average_rating / 5) * 100
                else:
                    service.average_rating_percent = 0

        return render(request, "promo/services_list.html", {"types": types})


class ServiceReviewListView(ListView):
    """Список отзывов на конкретную услугу с проверками прав на спам"""

    template_name = "promo/service_review_list.html"
    context_object_name = "reviews"

    def get_queryset(self):
        service = get_object_or_404(Service, id=self.kwargs["service_id"])
        # Тянем только одобренные админом отзывы, подгружая авторов для оптимизации SQL
        return Review.objects.filter(
            service=service, status="published"
        ).select_related("author")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = get_object_or_404(Service, id=self.kwargs["service_id"])
        context["service"] = service

        # Защита от анонимных пользователей (AnonymousUser)
        if self.request.user.is_authenticated:
            # Проверяем, оставлял ли пользователь отзыв ранее
            context["user_has_reviewed"] = Review.objects.filter(
                service=service, author=self.request.user
            ).exists()
            # Проверяем, покупал ли пользователь услугу хотя бы раз
            context["user_has_used"] = Purchase.objects.filter(
                user=self.request.user, service=service, ever_used=True
            ).exists()
        else:
            # Гости не могут спамить и оставлять отзывы
            context["user_has_reviewed"] = False
            context["user_has_used"] = False

        return context


class CreatePaymentOrderView(LoginRequiredMixin, FormView):
    """Создание заказа на оплату"""
    template_name = 'promo/payment_form.html'
    form_class = PaymentOrderForm
    
    def dispatch(self, request, *args, **kwargs):
        self.service = get_object_or_404(Service, id=self.kwargs['service_id'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service'] = self.service
        return context
    
    def form_valid(self, form):
        ad = form.cleaned_data['ad']
        comment = form.cleaned_data['comment']
        
        payment_order = PaymentOrder.objects.create(
            user=self.request.user,
            service=self.service,
            ad=ad,
            amount=self.service.price,
            comment=comment,
            status='pending'
        )
        
        return redirect('promo:process_payment', order_id=payment_order.id)
    
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class ProcessPaymentView(LoginRequiredMixin, View):
    """Обработка платежа: создание ссылки на YooKassa"""
    
    def get(self, request, order_id):
        payment_order = get_object_or_404(
            PaymentOrder,
            id=order_id,
            user=request.user,
            status='pending'
        )
        
        try:
            payment_service = YooKassaPaymentService()
            payment_data = payment_service.create_payment(payment_order)
            return redirect(payment_data['confirmation_url'])
        except Exception as e:
            messages.error(request, f"Ошибка создания платежа: {e}")
            return redirect('promo:services_list')


class PaymentCallbackView(LoginRequiredMixin, View):
    """Callback после оплаты (возврат с YooKassa)"""
    
    def get(self, request):
        order_id = request.GET.get('order_id')
        if order_id:
            try:
                payment_order = PaymentOrder.objects.get(id=order_id, user=request.user)
                if payment_order.status == 'paid':
                    messages.success(request, f"Оплата прошла успешно! Услуга активирована.")
                else:
                    messages.info(request, "Платёж обрабатывается. Услуга будет активирована в ближайшее время.")
            except PaymentOrder.DoesNotExist:
                messages.error(request, "Заказ не найден")
        
        return redirect('users:profile', username=request.user.username)
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render


class FavoriteMixin:
  def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_authenticated:
            # Получаем список ID объявлений, которые попали в текущую выборку (List/Detail)
            current_ads = context.get('ads') or ([context.get('ad')] if context.get('ad') else [])
            current_ad_ids = [ad.id for ad in current_ads if ad]

            # Тянем из базы только те ID избранного, которые есть на экране
            context['favorite_ids'] = list(
                user.favorites.filter(ad_id__in=current_ad_ids)
                .values_list('ad_id', flat=True)
            )
        else:
            context['favorite_ids'] = []
        return context
  
  
class OwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        # Проверяем, залогинен ли и является ли владельцем
        return self.request.user.is_authenticated and obj.owner == self.request.user

    def handle_no_permission(self):
        # Если юзер не залогинен — кидаем на логин, если залогинен, но не автор — 403
        if not self.request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(self.request.get_full_path())
        return render(self.request, 'ads/pages/not_allowed.html', status=403)
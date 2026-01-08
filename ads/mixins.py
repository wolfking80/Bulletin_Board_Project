class FavoriteMixin:
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    if self.request.user.is_authenticated:
      context['favorite_ids'] = list(
          self.request.user.favorites.values_list('ad_id', flat=True)
          )
    else:
      context['favorite_ids'] = []
    return context
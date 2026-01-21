class FavoriteMixin:
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)  # просим родителя собрать его стандартные данные, чтобы ничего не потерять
    if self.request.user.is_authenticated:        # проверка, залогинен ли пользователь
      context['favorite_ids'] = list(             # создаем в контексте переменную favorite_ids, в которую положим список ID объявлений
                                                  # оборачиваем в list(), чтобы превратить запрос в обычный список чисел
          self.request.user.favorites.values_list('ad_id', flat=True)   # обращаемся к пользователю, затем к его избранному
          )                                       # просим базу данных выдать нам не целые объекты, а только ID объявлений
                                                  # параметр flat=True превращает результат из списка кортежей [(1,), (5,)] в плоский список [1, 5]
    else:
      context['favorite_ids'] = []                # если пользователь аноним, мы отдаем пустой список
    return context
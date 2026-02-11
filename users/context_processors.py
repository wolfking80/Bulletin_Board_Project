def current_theme(request):
  if request.user.is_authenticated:
    return {'current_theme': request.user.selected_theme}

  return {'current_theme': request.session.get('theme', 'dark')}
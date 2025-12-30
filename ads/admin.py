from django.contrib import admin

from ads.models import Advertisement, Category, SubCategory, Tag


admin.site.register(Advertisement)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Tag)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import MyUserChangeForm
from .models import User


class MyUserAdmin(UserAdmin):
    form = MyUserChangeForm


admin.site.register(User, MyUserAdmin)

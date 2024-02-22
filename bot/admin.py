from django.contrib import admin

from bot.models import EEUser, Task


@admin.register(EEUser)
class EEUserAdmin(admin.ModelAdmin):
    pass


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass

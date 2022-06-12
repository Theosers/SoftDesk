from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Projects, Users, Issues, Comments, Contributors


class UsersAdmin(UserAdmin):
    ordering = ('email', )
    list_filter = ('staff', )


admin.site.register(Projects)

admin.site.register(Users, UsersAdmin)
admin.site.register(Issues)
admin.site.register(Comments)
admin.site.register(Contributors)


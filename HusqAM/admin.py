from django.contrib import admin
from .models import Robot


class RobotAdmin(admin.ModelAdmin):
	list_display = ('owner', 'manufac_id', 'manufac_model', 'given_name')

admin.site.register(Robot, RobotAdmin)

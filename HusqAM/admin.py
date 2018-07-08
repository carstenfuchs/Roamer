from django.contrib import admin
from .models import Robot, Status


class RobotAdmin(admin.ModelAdmin):
    list_display = ('owner', 'manufac_id', 'manufac_model', 'given_name')

admin.site.register(Robot, RobotAdmin)


class StatusAdmin(admin.ModelAdmin):
    list_display = (
        "robot",
        "timestamp",
        "batteryPercent",
        "connected",
        "lastErrorCode",
        "lastErrorTimestamp",
        "mowerStatus",
        "nextStartSource",
        "nextStartTimestamp",
        "operatingMode",
        "storedTimestamp",
        "showAsDisconnected",
        "valueFound",
    )

admin.site.register(Status, StatusAdmin)

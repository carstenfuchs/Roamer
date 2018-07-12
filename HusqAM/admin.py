from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Robot, Status


class RobotAdmin(admin.ModelAdmin):
    def link_to_daily_page(self, robot):
        return format_html('<a href="{}">daily</a>'.format(reverse("husqam:robot-daily", args=(robot.id,))))
    link_to_daily_page.short_description = "Activity"

    list_display = ('owner', 'manufac_id', 'manufac_model', 'given_name', 'link_to_daily_page')

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

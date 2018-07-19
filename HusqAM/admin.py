from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html
from .models import HusAccount, Robot, Status


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


# Erweitere die eingebaute "User"-Änderungsseite um Berücksichtigung des Husqvarna Accounts.
class HusAccount_Inline(admin.TabularInline):
    model = HusAccount

class RoamerUserAdmin(UserAdmin):
    # list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'last_login', LinkAufMA]
    inlines = (HusAccount_Inline,)

# Ersetze die __unicode__ Methode der User-Klasse wie unter
#   - http://stackoverflow.com/questions/11902262/django-user-full-name-as-unicode
#   - http://stackoverflow.com/questions/5062493/override-django-user-model-unicode
# vorgeschlagen.
#def user_new_unicode(self):
#    return u"{}, {}".format(self.last_name, self.first_name) # + (u" (Admin)" if self.is_superuser else u"")
#User.__unicode__ = user_new_unicode

admin.site.unregister(User)
admin.site.register(User, RoamerUserAdmin)

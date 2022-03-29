from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class HusAccount(models.Model):
    """
    This class represents one "Connect" account at Husqvarna.
    Each such account is normally owned by exactly one individual person,
    so that we associate it with exactly one of our User accounts.
    Querying one Husqvarna account returns information about all robots that
    are paired with it, however note that one robot can be paired to multiple
    accounts: Querying two accounts can return updates about a common robot.
    """
    user           = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    hus_login      = models.CharField(max_length=60)
    hus_password   = models.CharField(max_length=60)
    token_id       = models.CharField(max_length=60, blank=True)
    token_provider = models.CharField(max_length=60, blank=True)
    token_expires  = models.DateTimeField(null=True, blank=True)

    def update_connection(self, mowAPI, force_new_token=False):
        if force_new_token:
            self.token_id = ""

        if self.token_id and self.token_provider and self.token_expires and timezone.now() < self.token_expires:
            mowAPI.set_token(self.token_id, self.token_provider)
            return False

        expires = mowAPI.login(self.hus_login, self.hus_password)

        self.token_id = mowAPI.token
        self.token_provider = mowAPI.provider
        self.token_expires = timezone.now() + timedelta(0, expires)
        self.save()
        return True


class Robot(models.Model):
    id            = models.AutoField(primary_key=True)
    owner         = models.ForeignKey(User, models.PROTECT)
    manufac_id    = models.CharField(max_length=60, unique=True)
    manufac_model = models.CharField(max_length=60, blank=True)
    given_name    = models.CharField(max_length=80, blank=True)
    anon_id       = models.CharField(max_length=10, null=True, blank=True, unique=True, default=None, help_text="The robot's ID that is used for sharing through a private link.")

    def update_from_dict(self, d):
        """
        Updates this Robot instance with the information in dict `d`.
        """
        assert self.manufac_id == d['id']
        changed = []

        for (model_fieldname, dict_key) in (("manufac_model", "model"), ("given_name", "name")):
            if dict_key in d and getattr(self, model_fieldname) != d[dict_key]:
                setattr(self, model_fieldname, d[dict_key])
                changed.append(model_fieldname)

        return changed

    def __str__(self):
        return "{}".format(self.given_name or self.manufac_model or self.id)


class Status(models.Model):
    id                 = models.AutoField(primary_key=True)
    robot              = models.ForeignKey(Robot, models.CASCADE)
    timestamp          = models.DateTimeField(auto_now_add=True)

    batteryPercent     = models.SmallIntegerField()
    connected          = models.BooleanField()
    lastErrorCode      = models.SmallIntegerField()
    lastErrorTimestamp = models.DateTimeField(null=True, blank=True)
    mowerStatus        = models.CharField(max_length=80)
    nextStartSource    = models.CharField(max_length=80)
    nextStartTimestamp = models.DateTimeField(null=True, blank=True)
    operatingMode      = models.CharField(max_length=40)    # always "AUTO"
    storedTimestamp    = models.DateTimeField()
    showAsDisconnected = models.BooleanField()      # always False
    valueFound         = models.BooleanField()      # always True

    def update_from_dict(self, d):
        """
        Updates this Status instance with the information in dict `d`.
        """
        changed = []

        for (model_fieldname, dict_key) in (
            ("batteryPercent", "batteryPercent"),
            ("connected", "connected"),
            ("lastErrorCode", "lastErrorCode"),
            ("lastErrorTimestamp", "lastErrorCodeTimestamp"),
            ("mowerStatus", "mowerStatus"),
            ("nextStartSource", "nextStartSource"),
            ("nextStartTimestamp", "nextStartTimestamp"),
            ("operatingMode", "operatingMode"),
            ("storedTimestamp", "storedTimestamp"),
            ("showAsDisconnected", "showAsDisconnected"),
            ("valueFound", "valueFound"),
        ):
            if dict_key in d and getattr(self, model_fieldname) != d[dict_key]:
                if dict_key == "storedTimestamp":
                    val = datetime.fromtimestamp(d[dict_key] / 1000.0, timezone.utc)
                elif dict_key.endswith("Timestamp"):
                    val = datetime.fromtimestamp(d[dict_key], timezone.utc) if d[dict_key] else None
                else:
                    val = d[dict_key]

                setattr(self, model_fieldname, val)
                changed.append(model_fieldname)

        return changed

    def is_relevant_change(self, prevStatus):
        """
        Is this status a relevant change compared to the previous status?
        """
        return (
            self.connected != prevStatus.connected or
            self.lastErrorCode != prevStatus.lastErrorCode or
            self.mowerStatus != prevStatus.mowerStatus or
            self.nextStartSource != prevStatus.nextStartSource or
            self.operatingMode != prevStatus.operatingMode or
            self.showAsDisconnected != prevStatus.showAsDisconnected or
            self.valueFound != prevStatus.valueFound
        )

    def should_save(self):
        try:
            prevStatus = Status.objects.filter(robot=self.robot).latest("timestamp")
        except Status.DoesNotExist:
            return True

        return self.is_relevant_change(prevStatus)

    class Meta:
        ordering = ["timestamp"]
        verbose_name_plural = "Status"

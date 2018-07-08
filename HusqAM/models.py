from datetime import datetime, timezone
from django.contrib.auth.models import User
from django.db import models


class Robot(models.Model):
    id            = models.AutoField(primary_key=True)
    owner         = models.ForeignKey(User, models.PROTECT)
    manufac_id    = models.CharField(max_length=60, unique=True)
    manufac_model = models.CharField(max_length=60, blank=True)
    given_name    = models.CharField(max_length=80, blank=True)

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
        return "{} ({})".format(self.given_name or self.manufac_model or self.id, self.manufac_id)


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
    nextStartTimestamp = models.DateTimeField()
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

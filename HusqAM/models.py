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

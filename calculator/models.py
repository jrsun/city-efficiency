from django.db import models

class City(models.Model):
    lat = models.FloatField(blank=False, null=False)
    lng = models.FloatField(blank=False, null=False)
    eff = models.FloatField(blank=False, null=False)
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return " %s" % self.name

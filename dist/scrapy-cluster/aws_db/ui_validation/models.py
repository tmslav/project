from django.db import models

class Results(models.Model):
    timestamp = models.TimeField(auto_now=True)
    parts_searched = models.IntegerField(default=0)
    parts_found = models.IntegerField(default=0)
    parts_not_found = models.IntegerField(default=0)
    percent_found = models.IntegerField(default=0)
    link = models.TextField(max_length=300,default="none")

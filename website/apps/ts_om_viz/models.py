from django.db import models

class Document(models.Model):
    file = models.FileField(upload_to='SurveyResults/')
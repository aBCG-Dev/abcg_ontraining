from django.db import models

class EptbSite(models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=250)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self):
        return self.name


class EptbSubQuestion(models.Model):
    site = models.ForeignKey(EptbSite, on_delete=models.CASCADE, related_name="sub_questions")
    code = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=500)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self):
        return f"{self.site.name} - {self.label[:50]}"

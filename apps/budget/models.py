from django.db import models


class Budget(models.Model):
    """Budget"""
    codename = models.CharField(verbose_name="Code name", max_length=255, primary_key=True)
    daily_limit = models.IntegerField(verbose_name="Daily limit")

    def __str__(self):
        return self.codename

    class Meta:
        verbose_name = "Budget"
        verbose_name_plural = "Budgets"

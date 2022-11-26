from django.db import models

from apps.categories.models import Category


class Expense(models.Model):
    """Expense"""
    amount = models.IntegerField(verbose_name="Amount")
    created_at = models.DateTimeField("When created expense", auto_now=True)
    category_codename = models.ForeignKey(to=Category, on_delete=models.CASCADE, blank=True, null=True)
    raw_text = models.CharField(max_length=255)

    def __str__(self):
        return self.category_codename.codename

    class Meta:
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"

from django.db import models


class Category(models.Model):
    """Category"""
    codename = models.CharField(verbose_name="Code name", max_length=255, primary_key=True)
    name = models.CharField("Category name", max_length=255)
    is_base_expense = models.BooleanField(default=True)
    aliases = models.CharField(max_length=255)

    def __str__(self):
        return self.codename

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

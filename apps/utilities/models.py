from django.db import models

class Country(models.Model):
    country_code = models.CharField(max_length=20, null=True, blank=True)
    country_name = models.CharField(max_length=225, null=True, blank=True)
    currency_code = models.CharField(max_length=20, null=True, blank=True)
    languages = models.CharField(max_length=225, null=True, blank=True)
    capital = models.CharField(max_length=225, null=True, blank=True)

    iso2 = models.CharField(max_length=20, unique=True, db_index=True)
    iso3 = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    iso_numeric = models.CharField(max_length=20, null=True, blank=True)

    telephone_prefix = models.CharField(max_length=20, null=True, blank=True)  # e.g. "+977"
    flag_png = models.URLField(null=True, blank=True)  # e.g. https://flagcdn.com/w80/np.png
    flag_svg = models.URLField(null=True, blank=True)  # e.g. https://flagcdn.com/np.svg

    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "countries"
        ordering = ["country_name"]

    def __str__(self):
        return f"{self.country_name} ({self.iso2})"
    

class Zone(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=255, null=True, blank=True)
    status = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "zones"
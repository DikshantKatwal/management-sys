from django.core.management.base import BaseCommand
from django.db import transaction

import requests
import pycountry
import phonenumbers

from apps.utilities.models import Country


# ----------------------------
# Helpers
# ----------------------------
def flagcdn_png(iso2: str) -> str:
    return f"https://flagcdn.com/w80/{iso2.lower()}.png"


def flagcdn_svg(iso2: str) -> str:
    return f"https://flagcdn.com/{iso2.lower()}.svg"


def calling_code_for_iso2(iso2: str):
    code = phonenumbers.country_code_for_region(iso2.upper())
    return f"+{code}" if code else None


# ----------------------------
# Command
# ----------------------------
class Command(BaseCommand):
    help = "Seed countries table with ISO, phone codes, flags, currency, language, capital."

    @transaction.atomic
    def handle(self, *args, **options):
        # 1️⃣ Fetch REST Countries (filtered fields)
        url = (
            "https://restcountries.com/v3.1/all"
            "?fields=cca2,capital,languages,currencies"
        )
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        rest_map = {}
        for rc in response.json():
            iso2 = rc.get("cca2")
            if not iso2:
                continue

            rest_map[iso2] = {
                "capital": ", ".join(rc.get("capital", [])),
                "languages": ", ".join(rc.get("languages", {}).values()),
                "currency_code": next(
                    iter(rc.get("currencies", {}).keys()), None
                ),
            }

        created = updated = 0

        # 2️⃣ Merge with pycountry ISO data
        for c in pycountry.countries:
            iso2 = getattr(c, "alpha_2", None)
            iso3 = getattr(c, "alpha_3", None)

            if not iso2 or not iso3:
                continue

            rest = rest_map.get(iso2, {})

            defaults = {
                # 🔑 FIXED HERE
                "country_code": iso2,          # <= max_length=2
                "country_name": c.name,

                "currency_code": rest.get("currency_code"),
                "languages": rest.get("languages"),
                "capital": rest.get("capital"),

                "iso2": iso2,
                "iso3": iso3,
                "iso_numeric": getattr(c, "numeric", None),

                "telephone_prefix": calling_code_for_iso2(iso2),
                "flag_png": flagcdn_png(iso2),
                "flag_svg": flagcdn_svg(iso2),

                "is_active": True,
            }

            obj, created_flag = Country.objects.update_or_create(
                iso2=iso2,
                defaults=defaults
            )

            if created_flag:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Countries seeded successfully: created={created}, updated={updated}"
            )
        )

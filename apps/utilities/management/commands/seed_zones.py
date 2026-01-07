from django.core.management.base import BaseCommand
from django.db import transaction

import pycountry

from apps.utilities.models import Country, Zone


def fit(value: str | None, max_len: int):
    if not value:
        return None
    return value[:max_len]


class Command(BaseCommand):
    help = "Seed zones (states/provinces) using ISO-3166-2 subdivisions."

    @transaction.atomic
    def handle(self, *args, **options):
        created = skipped = 0

        # Cache countries by ISO2
        country_map = {
            c.iso2: c
            for c in Country.objects.all()
            if c.iso2
        }

        for sub in pycountry.subdivisions:
            # subdivision.code → e.g. "NP-BAG", "AU-NSW"
            if not sub.code or "-" not in sub.code:
                continue

            iso2 = sub.code.split("-")[0]
            country = country_map.get(iso2)

            if not country:
                continue  # country not seeded

            name = fit(sub.name, 255)
            code = fit(sub.code, 255)

            # Avoid duplicates
            exists = Zone.objects.filter(
                country=country,
                code=code
            ).exists()

            if exists:
                skipped += 1
                continue

            Zone.objects.create(
                country=country,
                name=name,
                code=code,
                status=1
            )
            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Zones seeded successfully: created={created}, skipped={skipped}"
            )
        )

from rest_framework import serializers

from apps.utilities.models import Country, Zone


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = [
            "id",
            "country_name",
            "country_code",
            "languages",
            "languages",
            "telephone_prefix",
            "flag_png",
            "flag_svg",
            "iso3",
        ]


class ZoneSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(
        source="country.country_name",
        read_only=True
    )

    class Meta:
        model = Zone
        fields = [
            "id",
            "country",
            "country_name",
            "name",
            "code",
            "status",
        ]

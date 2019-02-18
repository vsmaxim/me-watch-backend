from rest_framework import serializers

from pictures.models import Link, Picture


class LinkSerializer(serializers.ModelSerializer):
    """Serializer for picture.Link model"""
    picture = serializers.SlugRelatedField(queryset=Picture.objects, slug_field="name")

    class Meta:
        model = Link
        fields = (
            'id',
            'season',
            'episode',
            'picture',
            'source',
        )

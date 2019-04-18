from rest_framework import serializers

from pictures.models import Link, Picture, Status


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


class StatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Status
        fields = (
            'episode',
            'season',
            'picture',
            'user',
            'finished',
        )


class StatusFinishMixin(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        instance.finished = True
        return super().update(instance, validated_data)


class StatusFinishSerializer(StatusFinishMixin, StatusSerializer):
    pass


class PictureListSerializer(serializers.ModelSerializer):
    status_set = StatusSerializer(many=True)

    class Meta:
        model = Picture
        fields = (
            'name',
            'type',
            'status_set',
        )

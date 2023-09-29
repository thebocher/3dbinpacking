from rest_framework import serializers

from .models import PalleteType, Pallete, Item


class PalleteTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PalleteType
        fields = '__all__'


class ActivePalleteSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)


class ItemRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = (
            'external_id', 'length', 'width', 'height', 'weight', 'need_edge_l',
            'complete_edge_l', 'need_edge_t', 'complete_edge_t', 'need_edge_r',
            'complete_edge_r', 'need_edge_b', 'complete_edge_b', 'xnc_need',
            'from_temp'
        )


class ItemResponseSerializer(serializers.ModelSerializer):
    pallete_type = serializers.IntegerField(source='pallete.type.id')
    can_put_temp_item_id = serializers.IntegerField(
        source='_can_put_temp_item_id', default=None
    )

    class Meta:
        model = Item
        fields = '__all__'


class PalleteSerializer(serializers.ModelSerializer):
    items = ItemResponseSerializer(
        source='item_set', many=True, read_only=True
    )

    class Meta:
        model = Pallete
        fields = '__all__'

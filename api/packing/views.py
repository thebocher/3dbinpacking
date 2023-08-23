from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.http import Http404

from .models import Item, Pallete, PalleteType
from .serializers import (
    ItemRequestSerializer, ItemResponseSerializer, 
    PalleteSerializer, ActivePalleteSerializer,
    PalleteTypeSerializer,
)
from .exceptions import (
    ActivePalleteWithTypeAbsent, ItemDoesntFitToPallete, 
    PalleteWillBeOverweight
)

from packing.pallet_packer import PalletPacker


class CreateListDestroyViewset(mixins.CreateModelMixin, 
                               mixins.RetrieveModelMixin,
                               mixins.DestroyModelMixin,
                               mixins.ListModelMixin, 
                               viewsets.GenericViewSet):
    pass


@extend_schema_view(
    list=extend_schema(
        description='Возвращает список существующих типов паллет'
    ),
    retrieve=extend_schema(
        description='Возвращает информацию о выбранной паллете'
    ),
    destroy=extend_schema(
        description=(
            'Удаляет выбранный тип паллеты. Так же удалятся паллеты с таким '
            'типом, и детали этих паллет'
        )
    ),
    create=extend_schema(description='Создаёт тип паллеты')
)
class PalleteTypeViewSet(CreateListDestroyViewset):
    queryset = PalleteType.objects.all()
    serializer_class = PalleteTypeSerializer
    permission_classes = [IsAuthenticated]


@extend_schema_view(
    list=extend_schema(
        description='Возвращает список существующих паллет'
    ),
    retrieve=extend_schema(
        description='Возвращает информацию о выбраной паллете'
    ),
    destroy=extend_schema(
        description=(
            'Удаляет выбранную паллету. Все детали в даной паллете тоже '
            'удалятся'
        )
    ),
    create=extend_schema(description='Создаёт паллету'),
    set_active=extend_schema(
        description=(
            'Делает паллету активной. Если уже существуют активные паллеты '
            'с таким же типом, как и выбранная, то они стают неактивными'
        )
    )
)
class PalleteViewSet(CreateListDestroyViewset):
    queryset = Pallete.objects.all()
    serializer_class = PalleteSerializer
    permission_classes = [IsAuthenticated]

    @action(
        detail=False, 
        methods=['post'], 
        serializer_class=ActivePalleteSerializer
    )
    def set_active(self, request, *args, **kwargs):
        serializer = ActivePalleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pallete_id = serializer.validated_data['id']

        try:
            pallete = Pallete.objects.get(id=pallete_id)
            (Pallete.objects
                .filter(active=True, type=pallete.type)
                .update(active=False))
            pallete.active = True
            pallete.save()
        except Pallete.DoesNotExist:
            raise Http404

        response_serializer = PalleteSerializer(instance=pallete)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


@extend_schema_view(
    create=extend_schema(
        request=ItemRequestSerializer,
        responses={
            201: ItemResponseSerializer,
            ItemDoesntFitToPallete.status_code: ItemDoesntFitToPallete,
            ActivePalleteWithTypeAbsent.status_code: ActivePalleteWithTypeAbsent
        },
        description=(
            'Создаёт деталь. Если need_edge==true и complete_edge==false у '
            "одной из сторон, тогда в ответ тип паллеты будет 'return'. "
            "Иначе, если xnc_need==true, то тип паллеты будет 'warehouse. "
            "Иначе, тип паллеты будет 'chpu'\n"
            "Если деталь не помещается в паллету, возвращается ошибка "
            "со статус кодом 406 и ключём ошибки. Если не удалось найти "
            "активную паллету с подходящим типом, то возвращается ошибка "
            "со статус кодом 404"
        )
    ),
    retrieve=extend_schema(
        description='Возвращает информацию о выбранной детали'
    ),
    destroy=extend_schema(
        description='Удаляет выбранную деталь'
    ),
    list=extend_schema(
        description='Возвращает список существующих деталей'
    )
)
class ItemViewSet(CreateListDestroyViewset):
    """"""
    queryset = Item.objects.all()
    serializer_class = ItemResponseSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # validating
        serializer = ItemRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.validated_data

        # getting pallete_type_name, based on item attrs
        sides = ['r', 't', 'l', 'b']
        pallete_type_name = 'chpu'
        
        for side in sides:
            need_edge = item[f'need_edge_{side}']
            complete_edge = item[f'complete_edge_{side}']

            if need_edge and not complete_edge:
                pallete_type_name = 'return'

        if item['xnc_need'] and pallete_type_name != 'return':
            pallete_type_name = 'warehouse'

        # getting appropriate active pallete
        palletes = (
            Pallete.objects
                .filter(active=True, type__name=pallete_type_name)
                .select_related('type')
                .prefetch_related('item_set')
        )

        if not palletes.exists():
            raise ActivePalleteWithTypeAbsent(pallete_type_name)

        pallete = palletes.first()
        pallete_current_weight = pallete.get_current_weight()

        if pallete.will_be_overweight(
                item['weight'], current_weight=pallete_current_weight):
            raise PalleteWillBeOverweight(
                pallete.id, pallete_current_weight, item['weight'],
                pallete.max_weight
            )

        item_model_instance = Item(
            external_id=item['external_id'],
            pallete=pallete,
            length=item['length'],
            width=item['width'],
            height=item['height'],
            weight=item['weight'],
            need_edge_l=item['need_edge_l'],
            need_edge_t=item['need_edge_t'],
            need_edge_r=item['need_edge_r'],
            need_edge_b=item['need_edge_b'],
            complete_edge_l=item['complete_edge_l'],
            complete_edge_t=item['complete_edge_t'],
            complete_edge_r=item['complete_edge_r'],
            complete_edge_b=item['complete_edge_b'],
            xnc_need=item['xnc_need'],
        )

        if pallete_type_name == 'return':
            item_model_instance.x = 0
            item_model_instance.y = 0
            item_model_instance.z = 0
            item_model_instance.rotate = 0
        else:
            # putting previous items and new item to packer and getting position
            # coordinates
            pallete_whd = pallete.length, pallete.width, pallete.height
            pallete_max_weight = pallete.max_weight
            packer = PalletPacker(pallete_whd, pallete_max_weight)

            for placed_item in pallete.item_set.all():
                whd = placed_item.length, placed_item.width, placed_item.height
                weight = placed_item.weight
                position = placed_item.x, placed_item.y, placed_item.z
                rotation_type = 1 if placed_item.rotate else 0
                packer.add_existing_item(whd, weight, position, rotation_type)

            new_item_whd = item['length'], item['width'], item['height']
            new_item_weight = item['weight']

            packer_item = packer.add_new_item(new_item_whd, new_item_weight)
            _, unfitted_items = packer.pack()

            if unfitted_items:
                raise ItemDoesntFitToPallete(pallete.id)

            x, y, z = packer_item.position
            item_model_instance.x = x
            item_model_instance.y = y
            item_model_instance.z = z
            item_model_instance.rotate = bool(packer_item.rotation_type)

            # saving item 
            item_model_instance.save()

        item_response_serializer = ItemResponseSerializer(
            instance=item_model_instance
        )
        return Response(
            item_response_serializer.data, status=status.HTTP_201_CREATED
        )


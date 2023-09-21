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
    queryset = Item.objects.all()
    serializer_class = ItemResponseSerializer
    permission_classes = [IsAuthenticated]

    @staticmethod
    def try_put_item(pallete, item: Item):
        pallete_whd = pallete.length, pallete.width, pallete.height
        pallete_max_weight = pallete.max_weight
        packer = PalletPacker(pallete_whd, pallete_max_weight)

        for placed_item in pallete.item_set.all():
            whd = (
                placed_item.length,
                placed_item.width,
                placed_item.height
            )
            weight = placed_item.weight
            position = placed_item.x, placed_item.y, placed_item.z
            rotation_type = 1 if placed_item.rotate else 0
            packer.add_existing_item(
                whd, weight, position, rotation_type
            )

        new_item_whd = (
            item.length, item.width, item.height
        )
        new_item_weight = item.weight

        packer_item = packer.add_new_item(
            new_item_whd, new_item_weight
        )
        
        _, unfitted_items = packer.pack()

        if unfitted_items:
            raise ItemDoesntFitToPallete(pallete.id)

        return packer_item.position, packer_item.rotation_type

    @staticmethod
    def get_pallete_type_name(item: Item):
        pallete_type_name = 'chpu'
        sides = ['r', 't', 'l', 'b']

        if item.xnc_need:
            pallete_type_name = 'warehouse'

        if ((item.length > 1100 or item.width > 600) 
                and not item.from_temp):
            pallete_type_name = 'temp'

        for side in sides:
            need_edge = getattr(item, f'need_edge_{side}')
            complete_edge = getattr(item, f'complete_edge_{side}')

            if need_edge and not complete_edge:
                pallete_type_name = 'return'
                break

        return pallete_type_name

    def get_pallete(self, item: Item):
        pallete_type_name = self.get_pallete_type_name(item)
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
                item.weight, current_weight=pallete_current_weight):
            raise PalleteWillBeOverweight(
                pallete.id, pallete_current_weight, item.weight,
                pallete.max_weight
            )
        return pallete

    def try_put_top_item_from_temp_pallete(self, temp_pallete):
        top_item = temp_pallete.get_top_item()

        if top_item is None:
            return
        
        pallete = self.get_pallete(top_item)

        try:
            self.try_put_item(pallete, top_item)
            return top_item.id
        except:
            return

    def create(self, request, *args, **kwargs):
        # validating
        serializer = ItemRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item_data = serializer.validated_data
        item = Item(**item_data)
        pallete = self.get_pallete(item)
        item.pallete = pallete

        if pallete.type.name == 'return':
            item.x = 0
            item.y = 0
            item.z = 0
            item.rotate = 0
        else:
            if pallete.type.name == 'temp':
                # putting item on top of the highest item
                # and in the center of pallete
                top_item = pallete.get_top_item()

                if top_item is None:
                    item_z = 0
                    item_height = 0
                else:
                    item_z = top_item.z
                    item_height = top_item.height
                
                item.x = (pallete.length - item.length) / 2
                item.y = (pallete.width - item.width) / 2
                item.z = item_z + item_height
                item.rotate = 0
            else:
                # putting previous items and new item to packer and getting 
                # position coordinates
                (x, y, z), rotation_type = self.try_put_item(
                    pallete, item
                )
                item.x = x
                item.y = y
                item.z = z
                item.rotate = bool(rotation_type)

            # saving item 
            item.save()

        temp_pallete = Pallete.objects.get(type__name='temp')

        # deleting item, which was placed from temp pallete
        if item.from_temp:
            temp_pallete_item = temp_pallete.item_set.filter(
                external_id=item.external_id
            )
            temp_pallete_item.delete()

        # trying to put item from temp pallete to other
        try:
            temp_item_id = self.try_put_top_item_from_temp_pallete(temp_pallete)
            item.can_put_temp_item_id = temp_item_id
        except:
            pass

        item_response_serializer = ItemResponseSerializer(
            instance=item
        )
        return Response(
            item_response_serializer.data, status=status.HTTP_201_CREATED
        )


from rest_framework.exceptions import APIException
from rest_framework import status

class ActivePalleteWithTypeAbsent(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = 'active_pallet_with_type_absent'

    def __init__(self, pallete_type_name):
        self.detail = (
            f'Pallete with type name \'{pallete_type_name}\' is '
            'not active or not created'
        )


class ItemDoesntFitToPallete(APIException):
    status_code = status.HTTP_406_NOT_ACCEPTABLE
    default_code = 'item_doesnt_fit_to_pallete'

    def __init__(self, pallete_id):
        self.detail = (
            f'Item doesn\'t fit to pallete with '
            f'id {pallete_id}'
        )


class PalleteWillBeOverweight(APIException):
    status_code = status.HTTP_406_NOT_ACCEPTABLE
    default_code = 'pallete_will_be_overweight'

    def __init__(
            self, pallete_id, pallete_current_weight, item_weight, 
            pallete_max_weight
        ):
        self.detail = (
            f'Pallete(id={pallete_id}) will be overweight. '
            f'Pallete current weight {pallete_current_weight}, '
            f'item weight {item_weight}, '
            f'pallete max weight {pallete_max_weight}'
        )


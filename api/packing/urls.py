from rest_framework.routers import DefaultRouter

from .views import PalleteViewSet, PalleteTypeViewSet, ItemViewSet


router = DefaultRouter(trailing_slash=False)
router.register(
    'pallete-types', PalleteTypeViewSet, basename='pallete_type'
)
router.register('palletes', PalleteViewSet, basename='pallete')
router.register('items', ItemViewSet, basename='item')

urlpatterns = router.urls

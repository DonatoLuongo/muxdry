from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import ReviewViewSet, submit_review_view

router = SimpleRouter()
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('product/submit/', submit_review_view, name='submit_review'),
    path('', include(router.urls)),
]

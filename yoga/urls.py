from django.urls import path
from . import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


urlpatterns = [
    path('', views.HelloWorld.as_view(), name='home'),
    path('get-slots/', views.YogaBatchView.as_view(), name='get_slots'),
    path('yoga-booking/', views.YogaBookingView.as_view(), name='yoga_booking'),
    path('payment/', views.PaymentView.as_view(), name="payment"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="schema-docs",
    ),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
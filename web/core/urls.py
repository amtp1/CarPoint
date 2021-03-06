from django.urls import path, register_converter

from django.conf import settings
from django.conf.urls.static import static

from .views import *
from .converts import *

register_converter(FloatUrlParameterConverter, "float")
register_converter(BooleanUrlParameterConverter, "bool")

urlpatterns = [
    # ===WEB urls==
    # Main urls.
    path("", Web.index, name="index"),

    # ===API urls===
    path("api/create_user/<int:user_id>/<str:first_name>/<str:username>", API.CreateBotUserView.as_view(), name="create_bot_user"),
    path("api/set_name/<int:user_id>/<str:name>", API.SetNameView.as_view(), name="set_name"),
    path("api/set_city/<int:user_id>/<str:city>", API.SetCityView.as_view(), name="set_city"),
    path("api/check_phone/<int:user_id>", API.CheckPhoneView.as_view(), name="check_phone"),
    path("api/set_phone/<int:user_id>/<int:phone>", API.SetPhoneView.as_view(), name="set_phone"),
    path("api/get_all_marks", API.GetAllMarksView.as_view(), name="get_all_marks"),
    path("api/get_all_bodies/<str:mark>", API.GetAllBodiesView.as_view(), name="get_all_bodies"),
    path("api/get_all_fuel_types/<str:mark>", API.GetAllFuelTypesView.as_view(), name="get_all_fuel_types"),
    path("api/find_car/<str:body>/<str:fuel_type>/<str:transmission>", API.FindCarView.as_view(), name="find_car")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
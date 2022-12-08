import re
import csv
import codecs
import traceback
from collections import Counter
from typing import Any
from time import sleep

from loguru import logger
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from rest_framework.generics import ListAPIView
from django.contrib.sessions.models import Session
from django.http import HttpRequest, HttpResponse, JsonResponse, HttpResponsePermanentRedirect

from core.models import *
from core.converts import str_to_bool, str_to_null
from core.tg.request import sendQuestion, leaveRequest
from core.utils.ip import get_client_ip
from core.utils.price import set_min_price, increase_price
from core.utils.car import sort_cars


PRICE_RANGE: dict = {
    "1": {
        "min": 500000,
        "max": 2000000
    },

    "2": {
        "min": 2000000,
        "max": 4000000
    },

    "3": {
        "min": 4000000,
        "max": 6000000
    },

    "4": {
        "min": 6000000,
        "max": 0
    },
}  # Keys is ids price range.


class APITemp:
    class CreateBotUserView(ListAPIView):
        serializer_class: BotUser = BotUser  # Set serializer object.

        def get(self, request: HttpRequest, user_id: int, first_name: str, username: str) -> JsonResponse:
            user: QuerySet = BotUser.objects.filter(user_id=user_id)

            if not user.exists():
                BotUser.objects.create(user_id=user_id, first_name=first_name, username=username)
                return JsonResponse({"response": True})
            user = user.get()
            return JsonResponse({"response": False, "name": user.name, "city": user.city_id})

    class SetNameView(ListAPIView):
        serializer_class: BotUser = BotUser

        def get(self, request: HttpRequest, user_id: int, name: str) -> JsonResponse:
            user: QuerySet = BotUser.objects.filter(user_id=user_id)
            user.update(name=name)
            return JsonResponse({"response": True})

    class SetCityView(ListAPIView):
        serializer_class: BotUser = BotUser

        def get(self, request: HttpRequest, user_id: int, city: str) -> JsonResponse:
            queryset: QuerySet = BotUser.objects.filter(user_id=user_id)
            city: QuerySet = City.objects.filter(title=city)

            if not city:
                return JsonResponse({"response": False})
            else:
                city = city.get()
                queryset.update(city_id=city.pk)
                return JsonResponse({"response": True, "message": city.message})

    class CheckPhoneView(ListAPIView):
        serializer_class: BotUser = BotUser

        def get(self, request: HttpRequest, user_id: int) -> JsonResponse:
            queryset: QuerySet = BotUser.objects.get(user_id=user_id)

            if queryset.phone:
                return JsonResponse({"response": True})
            else:
                return JsonResponse({"response": False})

    class SetPhoneView(ListAPIView):
        serializer_class: BotUser = BotUser

        def get(self, request: HttpRequest, user_id: int, phone: int) -> JsonResponse:
            queryset: QuerySet = BotUser.objects.filter(user_id=user_id)
            queryset.update(phone=phone)
            return JsonResponse({"response": True})

    class GetAllMarksView(ListAPIView):
        serializer_class: BotUser = BotUser

        def get(self, request: HttpRequest, min_price: int, max_price: int) -> JsonResponse:
            if max_price == 0:
                min_price, max_price = increase_price(min_price)
                marks = Car.objects.filter(price__range=[min_price, max_price]).values("mark__title").distinct()
            else:
                marks = Car.objects.filter(price__range=[min_price, max_price]).values("mark__title").distinct()
            all_marks = [mark.get("mark__title") for mark in marks]
            return JsonResponse({"all_marks": all_marks})

    class GetAllBodiesView(ListAPIView):
        serializer_class: Model = Model

        def get(self, request: HttpRequest, mark: str, min_price: int, max_price: int) -> JsonResponse:
            if mark != "any":
                mark = Mark.objects.get(title=mark)
            else:
                mark = None
            if max_price == 0:
                min_price, max_price = increase_price(min_price)
                if not mark:
                    car_filter = Car.objects.filter(price__range=[min_price, max_price])
                else:
                    car_filter = Car.objects.filter(mark=mark, price__lte=min_price)
            else:
                if not mark:
                    car_filter = Car.objects.filter(price__range=[min_price, max_price])
                else:
                    car_filter = Car.objects.filter(mark=mark, price__range=[min_price, max_price])

            if car_filter.exists():
                cars = car_filter.all()
                bodies = [car.set.model.body for car in cars]
                counter = Counter(bodies)
                bodies = list(counter.keys())
                return JsonResponse({"all_bodies": bodies})
            else:
                return JsonResponse({"all_bodies": []})

    class GetAllFuelTypesView(ListAPIView):
        serializer_class: Engine = Engine

        def get(self, request: HttpRequest, mark: str, body: str, min_price: int, max_price: int) -> JsonResponse:
            if max_price == 0:
                if mark == "any":
                    cars: QuerySet = Car.objects.filter(price__lte=min_price).all()
                else:
                    mark: QuerySet = Mark.objects.filter(title=mark).get()
                    cars: QuerySet = Car.objects.filter(mark=mark, price__lte=min_price).all()
            else:
                if mark == "any":
                    cars: QuerySet = Car.objects.filter(price__range=[min_price, max_price]).all()
                else:
                    mark: QuerySet = Mark.objects.filter(title=mark).get()
                    cars: QuerySet = Car.objects.filter(mark=mark, price__range=[min_price, max_price]).all()
            engines = [car.engine.type_fuel for car in cars if car.set.model.body == body]
            counter = Counter(engines)
            fuel_types = list(counter.keys())
            return JsonResponse({"all_fuel_types": fuel_types})

    class FindCarView(ListAPIView):
        serializer_class: Car = Car

        def get(self, request: HttpRequest, body: str,
                fuel_type: str) -> JsonResponse:
            headers = request.headers
            try:
                is_any: bool = False
                mark = str_to_null(headers.get("Mark"))
                min_p = headers.get("Min-Price")
                max_p = headers.get("Max-Price")
                if str_to_bool(headers.get("Is-Volume")):
                    min_volume = float(headers.get("Min-Volume"))
                    max_volume = float(headers.get("Max-Volume"))
                    if int(max_p) == 0:
                        min_price, max_price = increase_price(min_p)
                        cars = Car.objects.filter(price__range=[min_price, max_price],
                                                  engine__volume__range=[min_volume, max_volume]).all()
                    else:
                        cars = Car.objects.filter(price__range=[min_p, max_p], set__model__body=body,
                                                  engine__volume__range=[min_volume, max_volume]).all()
                    if cars:
                        if str_to_bool(headers.get("Is-Any-Fuel-Type")):
                            if mark:
                                mark = Mark.objects.filter(title=mark).get()
                                cars = [car.to_dict() for car in cars if car.mark_id == mark.pk]
                            else:
                                cars = [car.to_dict() for car in cars]
                                is_any = True
                        else:
                            if mark:
                                mark = Mark.objects.filter(title=mark).get()
                                cars = [car.to_dict() for car in cars
                                        if car.engine.type_fuel == fuel_type and car.mark_id == mark.pk]
                            else:
                                cars = [car.to_dict() for car in cars if car.engine.type_fuel == fuel_type]
                                is_any = True
                        return JsonResponse({"response": True, "is_any": is_any, "cars": cars})
                elif str_to_bool(headers.get("Is-Power")):
                    min_power: int = int(headers.get("Min-Power"))
                    max_power: int = int(headers.get("Max-Power"))
                    if int(max_p) == 0:
                        min_price, max_price = increase_price(min_p)
                        cars = Car.objects.filter(price__range=[min_price, max_price],
                                                  engine__power__range=[min_power, max_power],
                                                  set__model__body=body).all()
                    else:
                        cars = Car.objects.filter(price__range=[min_p, max_p],
                                                  engine__power__range=[min_power, max_power],
                                                  set__model__body=body).all()
                    if cars:
                        if str_to_bool(headers.get("Is-Any-Fuel-Type")):
                            if mark:
                                mark = Mark.objects.filter(title=mark).get()
                                cars = [car.to_dict() for car in cars if car.mark_id == mark.pk]
                            else:
                                cars = [car.to_dict() for car in cars]
                                is_any = True
                        else:
                            if mark:
                                mark = Mark.objects.filter(title=mark).get()
                                cars = [car.to_dict() for car in cars
                                        if car.engine.type_fuel == fuel_type and car.mark_id == mark.pk]
                            else:
                                cars = [car.to_dict() for car in cars if car.engine.type_fuel == fuel_type]
                                is_any = True
                        return JsonResponse({"response": True, "is_any": is_any, "cars": cars})
            except Exception as e:
                logger.error(e)
                return JsonResponse({"response": True, "cars": []})

    class GetCarInfoView(ListAPIView):
        serializer_class: Car = Car

        def get(self, request: HttpRequest, id: int) -> HttpResponse:
            car = Car.objects.get(id=id)
            return JsonResponse({"response": True, "car": car.to_dict()})

    class CreateEntryView(ListAPIView):
        serializer_class: Entry = Entry

        def get(self, request: HttpRequest, user_id: int, username: str, car_id: int,
                email: str, name: str, address: str, phone: int) -> JsonResponse:
            user = BotUser.objects.get(user_id=user_id)
            car = Car.objects.get(id=car_id)
            entry = Entry.objects.filter(user=user, username=username, car=car, email=email,
                                         name=name, address=address, phone=phone)
            if entry.exists():
                return JsonResponse({"response": False})
            else:
                entry = Entry.objects.create(user=user, username=username, car=car, email=email,
                                             name=name, address=address, phone=phone)
                setTypeCar = SetCarType.objects.filter(car=car)
                if setTypeCar.exists():
                    setTypeCar = setTypeCar.get()
                    distributor = Distributor.objects.get(distributor=setTypeCar.user)
                    set_entry = SetEntry.objects.create(distributor=distributor, entry=entry)
                    distributor_file = DistributorEntryFile.objects.create(entry=entry)
                    admin_file = AdminEntryFile.objects.create(entry=entry)
                    set_entry.distributor_file = distributor_file
                    set_entry.admin_file = admin_file
                    set_entry.save()
                return JsonResponse({"response": True})


class WebTemp:
    def index(request) -> HttpResponse:
        CAPTCHA_PUBLIC_KEY = settings.CAPTCHA_PUBLIC_KEY
        cities = City.objects.all()  # Get cities
        new_cars = NewCar.objects.all()  # Get new cars
        questions = Question.objects.all()  # Get questions
        # Init car config variables
        image: None = None
        main_length: int = 0
        min_price: int = 0
        cars: None = None
        # Get request values
        pricerange = request.GET.get("pricerange")
        mark = request.GET.get("mark")
        transmission = request.GET.get("transmission")
        body = request.GET.get("body")
        type_fuel = request.GET.get("type_fuel")
        volume = request.GET.get("volume")
        power = request.GET.get("power")
        cars = p_find_car(pricerange, mark, transmission, body, type_fuel, volume, power)

        if cars:
            cars_values = list(cars.values())
            main_length = sum([len(v["pattern"]) for v in cars_values])
            image = cars_values[0]["pattern"][0]["image"]
            min_price = min([car["pattern"][0]["price"] for car in cars_values])

        return render(request, "main/index.html",
                      dict(cities=cities, CAPTCHA_PUBLIC_KEY=CAPTCHA_PUBLIC_KEY,
                           new_cars=new_cars, questions=questions, cars=cars,
                           image=image, min_price=min_price, main_length=main_length, mark=mark))

    def oferta(request) -> JsonResponse:
        return render(request, "main/oferta.html")

    def get_cars(request, min_price: int, max_price: int, mark: str) -> JsonResponse:
        mark = Mark.objects.get(title=mark)  # Get mark obj
        if max_price == 0:
            min_price, max_price = increase_price(min_price)
            cars = Car.objects.filter(mark=mark, price__range=[min_price, max_price]).all()
        else:
            cars = Car.objects.filter(mark=mark, price__range=[min_price, max_price]).all()
        cars = sort_cars(cars, is_price=True)
        cars = [car.to_dict() for car in cars]
        return JsonResponse({"response": True, "cars": cars})

    def get_cars_by_body(request, min_price: int, max_price: int, mark: str, body: str) -> JsonResponse:
        mark = Mark.objects.get(title=mark)  # Get mark obj
        if max_price == 0:
            min_price, max_price = increase_price(min_price)
            cars = Car.objects.filter(mark=mark, price__range=[min_price, max_price],
                                      set__model__body=body).all()
        else:
            cars = Car.objects.filter(mark=mark, price__range=[min_price, max_price],
                                      set__model__body=body).all()
        cars = sort_cars(cars, is_price=True)
        cars = [car.to_dict() for car in cars]
        return JsonResponse({"response": True, "cars": cars})

    def get_cars_by_type_fuel(request, min_price: int, max_price: int,
                              mark: str, body: str, type_fuel: str) -> JsonResponse:
        mark = Mark.objects.get(title=mark)  # Get mark obj
        if max_price == 0:
            min_price, max_price = increase_price(min_price)
            cars = Car.objects.filter(mark=mark, price__range=[min_price, max_price],
                                      set__model__body=body).all()
        else:
            cars = Car.objects.filter(mark=mark, price__range=[min_price, max_price],
                                      set__model__body=body).all()
        cars = sort_cars(cars, is_price=True)
        cars = [car.to_dict() for car in cars if car.engine.type_fuel == type_fuel]
        return JsonResponse({"response": True, "cars": cars})

    def get_cars_by_transmission(request, min_price: int, max_price: int, mark: str, body: str,
                                 type_fuel: str, transmission: str) -> JsonResponse:
        mark = Mark.objects.get(title=mark)  # Get mark obj
        if max_price == 0:
            min_price, max_price = increase_price(min_price)
            cars = Car.objects.filter(mark=mark, price__range=[min_price, max_price],
                                      set__model__body=body).all()
        else:
            cars = Car.objects.filter(mark=mark, price__range=[min_price, max_price],
                                      set__model__body=body, transmission__title=transmission).all()
        cars = sort_cars(cars, is_price=True)
        cars = [car.to_dict() for car in cars if car.engine.type_fuel == type_fuel]
        return JsonResponse({"response": True, "cars": cars})

    def get_cars_by_engine_volume(request, min_price: int, max_price: int, mark: str, body: str,
                                  type_fuel: str, transmission: str, engine_volume: str) -> JsonResponse:
        mark = Mark.objects.get(title=mark)  # Get mark obj
        if max_price == 0:
            min_price, max_price = increase_price(min_price)
            cars = Car.objects.filter(mark=mark, price__range=[min_price, max_price],
                                      set__model__body=body, transmission__title=transmission,
                                      engine__volume__lte=engine_volume).all()
        else:
            cars = Car.objects.filter(mark=mark, price__range=[min_price, max_price], set__model__body=body,
                                      transmission__title=transmission, engine__volume__lte=engine_volume).all()
        cars = sort_cars(cars, is_price=True)
        cars = [car.to_dict() for car in cars if car.engine.type_fuel == type_fuel]
        return JsonResponse({"response": True, "cars": cars})

    def send_question(request) -> HttpResponsePermanentRedirect:
        client_ip = get_client_ip(request)
        client = WebUser.objects.filter(ip_address=client_ip)
        if not client.exists():
            WebUser.objects.create(ip_address=client_ip)
        else:
            client = client.get()
            if not client.is_blocked:
                name: Any = request.POST.get("name")
                tel: str = re.sub("[^0-9]", "", request.POST.get("tel"))
                text = request.POST.get("text")
                UserQuestion.objects.create(ip_address=client_ip, name=name, phone=tel, question=text)
                sendQuestion(name, tel, text)
        return redirect("/")

    def leave_request(request) -> JsonResponse:
        is_new = request.POST.get("is_new")
        car_id = request.POST.get("car_id")
        name = request.POST.get("name")
        city = request.POST.get("city")
        tel = re.sub("[^0-9]", "", request.POST.get("tel"))
        email = request.POST.get("email")
        address = request.POST.get("address")
        leaveRequest(car_id, name, city, tel, email, address, is_new)
        if is_new:
            car = NewCar.objects.get(id=car_id)
        else:
            car = Car.objects.get(id=car_id)
            entry = Entry.objects.create(car=car, email=email,
                                         name=name, address=address, phone=tel)
            setTypeCar = SetCarType.objects.filter(car=car)
            if setTypeCar.exists():
                setTypeCar = setTypeCar.get()
                distributor = Distributor.objects.get(distributor=setTypeCar.user)
                set_entry = SetEntry.objects.create(distributor=distributor, entry=entry)
                distributor_file = DistributorEntryFile.objects.create(entry=entry)
                admin_file = AdminEntryFile.objects.create(entry=entry)
                set_entry.distributor_file = distributor_file
                set_entry.admin_file = admin_file
                set_entry.save()
        return JsonResponse({"response": True})


class DistributorTemp:
    def distributor(request, cars=None, files=None):
        if request.user.is_superuser:
            return redirect("/admin")

        if not request.user.is_authenticated:
            # Return auth page
            return redirect("distributor/auth")

        session_key = request.COOKIES.get("sessionid")
        session = Session.objects.filter(session_key=session_key)
        if not session.exists():
            return redirect("auth")
        session = session.get()
        uid = session.get_decoded().get('_auth_user_id')
        user = User.objects.get(pk=uid)
        files = File.objects.filter(user=user).all()
        cars = SetCarType.objects.filter(user=user, car__isnull=False).all()
        return render(request, "distributor/index.html",
                      {"username": user.username, "full_name": user.get_full_name(),
                       "session_key": session_key, "cars": cars, "files": files})

    def auth(request):
        if request.user.is_authenticated:
            # Return main page
            return redirect("distributor")

        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            if not user.is_superuser:
                login(request, user)
                return redirect("distributor")
        return render(request, "distributor/auth.html")

    def logout_view(request):
        logout(request)
        return JsonResponse({"response": True})

    def upload_csv_file(request, n=0):
        if not request.user.is_authenticated:
            # Return main page
            return redirect("distributor")

        user = user_obj(request)
        distributor = Distributor.objects.filter(distributor=user)
        if not distributor.exists():
            return JsonResponse({"response": False, "type": "NotDistribAccount"})
        try:
            file = request.FILES.get("file")
            reader = csv.reader(codecs.iterdecode(file, 'utf-8'))
            for r in reader:
                if n >= 1:
                    (power, type_fuel, volume, transmission_id, wd_id, title,
                     price, body, mark_id, image, color) = r
                    try:
                        engine = Engine.objects.filter(volume=volume, power=power, type_fuel=type_fuel)
                        if not engine.exists():
                            engine = Engine.objects.create(volume=volume, power=power,
                                                           type_fuel=type_fuel)
                        else:
                            engine = engine.first()
                        car = Car.objects.filter(title=title, image=image, price=price,
                                                 engine=engine, transmission_id=transmission_id,
                                                 wd_id=wd_id, mark_id=mark_id)
                        if not car.exists():
                            model = Model.objects.create(mark_id=mark_id, title=title, price=price,
                                                         body=body, is_visible=True)
                            set = Set.objects.create(model=model, title=title, image=image)
                            car = Car.objects.create(title=title, set=set, image=image, price=price,
                                                     engine=engine, transmission_id=transmission_id,
                                                     wd_id=wd_id, mark_id=mark_id)
                            color_obj = Color.objects.filter(title=color)
                            if not color_obj.exists():
                                color_obj = Color.objects.create(title=color)
                            else:
                                color_obj = color_obj.get()
                            SetColor.objects.create(car=car, color=color_obj)
                            SetCarType.objects.create(
                                type="distributor", car=car, user=user)
                    except Exception as e:
                        logger.error(e)
                n += 1
            File.objects.create(file=file, user=user)
            sleep(1)
            return JsonResponse({"response": True})
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"response": False, "error_message": e})

    def profile(request):
        if not request.user.is_authenticated:
            # Return main page
            return redirect("distributor")

        user = user_obj(request)
        distributor = Distributor.objects.filter(distributor=user)
        if distributor.exists():
            distributor = distributor.get()
        return render(request, "distributor/profile.html",
                      {"username": user.username, "date_joined": user.date_joined, "distributor": distributor})

    def cars(request):
        if not request.user.is_authenticated:
            # Return main page
            return redirect("distributor")

        return render(request, "distributor/cars.html")

    def save_data(request):
        if not request.user.is_authenticated:
            # Return main page
            return redirect("distributor")

        title = request.POST.get("title")
        image = request.FILES.get("image")
        user = user_obj(request)
        distributor = Distributor.objects.filter(distributor=user)
        if not distributor.exists():
            Distributor.objects.create(distributor=user, title=title, image=image)
        else:
            distributor = distributor.get()
            distributor.title = title
            distributor.image = image
            distributor.save()
        return JsonResponse({"response": True})

    def orders(request):
        if not request.user.is_authenticated:
            # Return main page
            return redirect("distributor")

        user = user_obj(request)
        distributor = Distributor.objects.filter(distributor=user)
        if not distributor.exists():
            orders = []
        else:
            distributor = distributor.get()
            orders = SetEntry.objects.filter(distributor=distributor).all()
        return render(request, "distributor/orders.html", {"orders": orders})

    def upload_documents(request):
        if not request.user.is_authenticated:
            # Return main page
            return redirect("distributor")

        files = request.FILES
        data = request.POST
        id = data.get("id")
        act = files.get("act")
        agreement = files.get("agreement")
        bill = files.get("bill")
        entry = SetEntry.objects.get(id=id)
        entry.status = "shipped"
        entry.save()
        dFile = DistributorEntryFile.objects.get(
            entry=entry.entry)
        dFile.act = act
        dFile.agreement = agreement
        dFile.bill = bill
        dFile.save()

        return JsonResponse({"response": True})

    def distribEntryInfo(request):
        if not request.user.is_authenticated:
            # Return main page
            return redirect("distributor")

        id = request.POST.get("id")
        entry = SetEntry.objects.filter(
            pk=id).get().to_dict(is_distributor=True)
        return JsonResponse({"response": True, "entry": entry})

    def agreements(request):
        user = user_obj(request)
        distributor = Distributor.objects.filter(distributor=user)
        if not distributor.exists():
            agreements = []
        else:
            distributor = distributor.get()
            agreements = Agreements.objects.filter(distributor=distributor).all()
        return render(request, "distributor/agreements.html", {"agreements": agreements})


class DealerTemp:
    def index(request):
        new_cars = NewCar.objects.all()  # Get new cars
        return render(request, "dealer/dealer.html", dict(new_cars=new_cars))


def p_find_car(pricerange: str, mark: str, transmission: str, body: str,
               type_fuel: str, volume: str, power: str) -> list:
    if not pricerange or not mark or not transmission or not body or not type_fuel:
        return []
    else:
        price_range = PRICE_RANGE.get(pricerange)
        min_p = int(price_range.get("min"))
        max_p = int(price_range.get("max"))
        mark = Mark.objects.filter(title=mark).get()
        transmission = Transmission.objects.filter(title=transmission).get()
        if not volume and not power:
            return []
        elif volume:
            if max_p == 0:
                cars = Car.objects.filter(mark=mark, price__gte=min_p, engine__type_fuel=type_fuel,
                                          transmission=transmission, set__model__body=body,
                                          engine__volume__lte=volume).all()
            else:
                cars = Car.objects.filter(mark=mark, price__range=[min_p, max_p], engine__type_fuel=type_fuel,
                                          transmission=transmission, set__model__body=body,
                                          engine__volume__lte=volume).all()
        elif power:
            if max_p == 0:
                cars = Car.objects.filter(mark=mark, price__gte=min_p, engine__type_fuel=type_fuel,
                                          transmission=transmission, set__model__body=body,
                                          engine__power__lte=power).all()
            else:
                cars = Car.objects.filter(mark=mark, price__range=[min_p, max_p], engine__type_fuel=type_fuel,
                                          transmission=transmission, set__model__body=body,
                                          engine__power__lte=power).all()
        else:
            if max_p == 0:
                cars = Car.objects.filter(mark=mark, price__gte=min_p, engine__type_fuel=type_fuel,
                                          transmission=transmission, set__model__body=body, engine__power__lte=power,
                                          engine__volume__gte=volume).all()
            else:
                cars = Car.objects.filter(mark=mark, price__range=[min_p, max_p], engine__type_fuel=type_fuel,
                                          transmission=transmission, set__model__body=body, engine__power__lte=power,
                                          engine__volume__gte=volume).all()
        if cars:
            cars = [car.to_dict() for car in cars if car.set.model.body == body]
            dct_cars: dict = {}
            price_arr: list = []
            for car in cars:
                pattern = {"id": car["id"], "title": car["title"], "price": car["price"], "image": car["image"],
                           "engine_volume": car["engine"]["volume"], "engine_power": car["engine"]["power"],
                           "engine_type_fuel": car["engine"]["type_fuel"], "wd": car["wd"], "special": car["special"],
                           "transmission": car["transmission"], "body": car["body"], "set_title": car["set_title"]}
                if not car["model_title"] in dct_cars:
                    dct_cars[car["model_title"]] = {"pattern": [pattern]}
                    price_arr.append(car["price"])
                else:
                    if not car["price"] in price_arr:
                        dct_cars[car["model_title"]]["pattern"].append(pattern)
                        price_arr.append(car["price"])
            dct_cars = set_min_price(dct_cars)
            return dct_cars
        else:
            return []


def user_obj(request):
    session_key = request.COOKIES.get("sessionid")
    session = Session.objects.filter(session_key=session_key)
    if not session.exists():
        return redirect("auth")
    session = session.get()
    uid = session.get_decoded().get('_auth_user_id')
    user = User.objects.get(pk=uid)
    return user

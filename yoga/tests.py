from django.test import TestCase, Client
from django.urls import reverse
from .models import YogaBatch, YogaBooking, YogaTimings, Offer, Order
from .views import YogaBatchView, YogaBookingView, PaymentView
import json
from datetime import datetime

class CreateTestData:

    @staticmethod
    def create_yoga_batch(year = 2023, month = 1, *args, **kwargs):
        kwargs.update(
            {
                "year": year,
                "month": month,
            }
        )
        yoga_batch = YogaBatch.objects.create(**kwargs)
        return yoga_batch
    
    @staticmethod
    def create_offer(name = "test_offer", discount = 100, validity_count = 1, code = "test_offer", *args, **kwargs):
        kwargs.update(
            {
                "name": name,
                "discount": discount,
                "validity_count": validity_count,
                "code": code
            }
        )
        offer = Offer.objects.create(**kwargs)
        return offer
    
    @staticmethod
    def create_booking(yoga_batch, name = "test_user", email = "example@gmail.com", date_of_birth = "1990-01-01", *args, **kwargs):
        kwargs.update(
            {
                "name": name,
                "email": email,
                "date_of_birth": date_of_birth,
                "yoga_batch": yoga_batch
            }
        )
        booking = YogaBooking.objects.create(**kwargs)
        return booking
    
class YogaBatchViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.get_slots_url = reverse('get_slots')
        self.yoga_batch = CreateTestData.create_yoga_batch()

    def test_get_slots_check_default_slots_are_created(self):
        response = self.client.post(self.get_slots_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "No Slot Available")

        response = self.client.post(self.get_slots_url, data=json.dumps({"year": 2023, "month": 1}), content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 200)
        
        timings = data["timings"]

        # Define the expected timings
        expected_timings = [
            {
                "start_time": "06:00:00",
                "end_time": "07:00:00"
            },
            {
                "start_time": "07:00:00",
                "end_time": "08:00:00"
            },
            {
                "start_time": "08:00:00",
                "end_time": "09:00:00"
            },
            {
                "start_time": "17:00:00",
                "end_time": "18:00:00"
            }
        ]
        for expected_timing in expected_timings:
            found = False
            for timing in timings:
                start_time = datetime.strptime(timing["start_time"], "%Y-%m-%dT%H:%M:%SZ").strftime("%H:%M:%S")
                end_time = datetime.strptime(timing["end_time"], "%Y-%m-%dT%H:%M:%SZ").strftime("%H:%M:%S")

                if start_time == expected_timing["start_time"] and end_time == expected_timing["end_time"]:
                    found = True
                    break
            self.assertTrue(found, f"Expected timing {expected_timing} not found in response")
        

class YogaBookingViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.yoga_booking_url = reverse('yoga_booking')
        self.yoga_batch = CreateTestData.create_yoga_batch()

    def test_yoga_booking(self):
        data = {
            "name": "Test User",
            "date_of_birth": "01-01-1990",
            "email": "test@example.com",
            "yoga_timing": str(self.yoga_batch.timings.first().external_id)
        }
        response = self.client.post(self.yoga_booking_url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_date_of_birth_under_age_18(self):
        data = {
            "name": "Test User",
            "date_of_birth": "01-01-2010",
            "email": "test@example.com",
            "yoga_timing": str(self.yoga_batch.timings.first().external_id)
        }
        response = self.client.post(self.yoga_booking_url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    def test_date_of_birth_above_age_65(self):
        data = {
            "name": "Test User",
            "date_of_birth": "01-01-1950",
            "email": "test@example.com",
            "yoga_timing": str(self.yoga_batch.timings.first().external_id)
        }
        response = self.client.post(self.yoga_booking_url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

class PaymentViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.yoga_batch = CreateTestData.create_yoga_batch()
        self.offer = CreateTestData.create_offer()
        data = {
            "name": "Test User",
            "date_of_birth": "01-01-1990",
            "email": "test@example.com",
            "yoga_timing": str(self.yoga_batch.timings.first().external_id),
            "coupon_code": self.offer.code
        }
        response = self.client.post(reverse('yoga_booking'), data=json.dumps(data), content_type='application/json')
        self.order_id = response.json()["order"]

    def test_payment(self):
        order = Order.objects.get(external_id=self.order_id)
        self.assertEqual(order.status, "created")
        self.assertEqual(order.amount, 400)
        data = {
            "order_id": self.order_id
        }
        response = self.client.post(reverse("payment"), data=json.dumps(data), content_type='application/json')
        order.refresh_from_db()
        self.assertEqual(order.status, "paid")
        self.assertEqual(response.status_code, 200)

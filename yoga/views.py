from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework import mixins, status
from .models import YogaBatch, YogaBooking, YogaTimings, Offer, Order
import datetime
from .serializers import YogaBookingSerializer, YogaBatchSerializer
from django.db.models import F
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, OpenApiResponse, OpenApiExample, inline_serializer
from rest_framework import serializers
from django.core.mail import EmailMessage

def send_mail(email, subject, order):
    order_id = order.external_id
    yoga_batch = order.yoga_batch
    start_yoga_timing = order.yoga_timing.start_time.strftime("%I:%M %p")
    end_yoga_timing = order.yoga_timing.end_time.strftime("%I:%M %p")
    msg = EmailMessage(subject, f'Here is your order id {order_id}, kindly show it at Yoga Center to verify your session.<br>Yoga Batch: {yoga_batch}<br>Yoga Timing: {start_yoga_timing} - {end_yoga_timing}', 'collegeform.contact@gmail.com', (email,))
    msg.content_subtype = "html"
    msg.send()
    
    return "Email Sent"

class HelloWorld(GenericAPIView):
    @extend_schema(responses={200: None})
    def get(self, request):
        # Return a simple "Hello, world!" message
        return Response({"message": "Hello, world!"})


# Serializer for handling the request data for YogaBatchView
class YogaBatchRequestSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField()


class YogaBatchView(GenericAPIView):
    serializer_class = YogaBatchSerializer

    @extend_schema(
        request=YogaBatchRequestSerializer,
        parameters=[
            OpenApiParameter(
                name="year",
                type=OpenApiTypes.STR,
                description="Year for the yoga batch",
                required=True,
                examples=[
                    OpenApiExample(
                        "2023",
                        summary="A valid year",
                        value="2023",
                        description="This is a valid year",
                    ),
                ],
            ),
            OpenApiParameter(
                name="month",
                type=OpenApiTypes.STR,
                description="Month for the yoga batch",
                required=True,
                examples=[
                    OpenApiExample(
                        "12",
                        summary="A valid month",
                        value="12",
                        description="This is a valid month",
                    ),
                ],
            ),
        ],
        responses={
            200: OpenApiResponse(response=YogaBatchSerializer, description='Successful operation'),
            400: OpenApiResponse(description='Bad request (something invalid)'),
        },
    )
    def post(self, request, *args, **kwargs):
        # Extract year and month from the request data
        year = request.data.get("year")
        month = request.data.get("month")

        try:
            # Query the database for a YogaBatch with the specified year and month
            yoga_batch = YogaBatch.objects.get(year=year, month=month)
        except YogaBatch.DoesNotExist:
            # If no batch is found, return a response indicating no slot is available
            return Response({"message": "No Slot Available"})

        # Serialize the YogaBatch data and return it in the response
        data = self.serializer_class(yoga_batch).data
        return Response(data)


# Serializer for handling the request and response data for YogaBookingView
class YogaBookingRequestSerializer(serializers.Serializer):
    name = serializers.CharField()
    email = serializers.EmailField()
    date_of_birth = serializers.DateField(input_formats=['%d-%m-%Y'])
    yoga_timing = serializers.UUIDField()
    offer_code = serializers.CharField(required=False)


class YogaBookingResponseSerializer(serializers.Serializer):
    external_id = serializers.UUIDField()
    name = serializers.CharField()
    email = serializers.EmailField()
    date_of_birth = serializers.DateField()
    order = serializers.UUIDField()


class YogaBookingView(GenericAPIView, mixins.CreateModelMixin):
    serializer_class = YogaBookingSerializer

    @extend_schema(
        request=YogaBookingRequestSerializer,
        parameters=[
            OpenApiParameter(
                name="date_of_birth",
                type=OpenApiTypes.STR,
                description="Date of birth of the user",
                required=True,
                examples=[
                    OpenApiExample(
                        "01-01-1990",
                        summary="A valid date of birth",
                        value="01-01-1990",
                        description="This is a valid date of birth",
                    ),
                ]
            ),
        ],
        responses={
            200: OpenApiResponse(response=YogaBookingResponseSerializer, description='Successful operation'),
            400: OpenApiResponse(description='Bad request (something invalid)'),
        },
    )
    def post(self, request, *args, **kwargs):
        # Extract data from the request
        date_of_birth = request.data.get("date_of_birth")
        email = request.data.get("email")
        yoga_timing = request.data.get("yoga_timing")
        offer = request.data.get("coupon_code", None)

        # Check for the existence and validity of the provided offer code
        if offer:
            try:
                offer = Offer.objects.get(code=offer)
            except Offer.DoesNotExist:
                return Response({"message": "Invalid Coupon Code"}, status=status.HTTP_404_NOT_FOUND)
            if offer.validity_count == 0:
                return Response({"message": "Coupon Code Expired"}, status=status.HTTP_400_BAD_REQUEST)

        # Format the date_of_birth and update the request data
        if date_of_birth:
            date_of_birth = datetime.datetime.strptime(date_of_birth, "%d-%m-%Y").date()
            formatted_date = date_of_birth.strftime("%Y-%m-%d")
        request.data["date_of_birth"] = formatted_date

        try:
            # Query the database for the corresponding YogaTimings using the provided external_id
            yoga_timing = YogaTimings.objects.get(external_id=yoga_timing)
            # Update the request data with the corresponding YogaBatch ID
            request.data["yoga_batch"] = yoga_timing.batch.id
            # Get the associated YogaBatch
            yoga_batch = yoga_timing.batch
        except YogaTimings.DoesNotExist:
            return Response({"message": "Invalid Yoga Timing"}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Check if a YogaBooking with the same email and YogaBatch already exists and is paid
            yoga_booking_paid = YogaBooking.objects.get(email=email, yoga_batch=yoga_batch).is_paid
            if yoga_booking_paid:
                return Response({"message": "Already Booked"}, status=status.HTTP_400_BAD_REQUEST)
        except YogaBooking.DoesNotExist:
            pass

        # Call the create method to save the YogaBooking instance and return the response
        return super().create(request, *args, **kwargs)


# Serializer for handling the request data for PaymentView
class PaymentRequestSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()


class PaymentResponseSerializer(serializers.Serializer):
    message = serializers.CharField()


class PaymentView(GenericAPIView):
    @extend_schema(
        request=PaymentRequestSerializer,
        responses={
            200: OpenApiResponse(response=PaymentResponseSerializer, description='Successful operation'),
            400: OpenApiResponse(description='Bad request (something invalid)'),
            404: OpenApiResponse(description='Invalid Order ID'),
        },
    )
    def post(self, request, *args, **kwargs):
        # Extract the order_id from the request data
        order_id = request.data.get("order_id")

        try:
            # Query the database for the corresponding Order using the provided external_id
            order = Order.objects.get(external_id=order_id)
            # Check if the order is already paid
            if order.status == "paid":
                return Response({"message": "Already Paid"}, status=status.HTTP_400_BAD_REQUEST)
            # Update the order status to "paid"
            order.status = "paid"
            order.save(update_fields=["status"])
            # Get the associated offer (if any) and update its validity count
            offer = order.offer
            if offer:
                offer.validity_count = F("validity_count")
                offer.validity_count = F("validity_count") - 1
                offer.save(update_fields=["validity_count"])
        except Order.DoesNotExist:
            # If the order with the provided order_id doesn't exist, return a 404 response
            return Response({"message": "Invalid Order ID"}, status=status.HTTP_404_NOT_FOUND)

        # Send email to the user
        send_mail(order.yoga_booking.email, 'Yoga Payment Received!', order)
        # Return a success message indicating that the payment was successful
        return Response({"message": "Payment Successful"})
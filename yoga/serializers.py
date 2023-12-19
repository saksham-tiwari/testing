# Import necessary modules and classes
from rest_framework import serializers
from .models import YogaBatch, YogaBooking, YogaTimings, Order, Offer
import datetime

# Serializer for handling YogaBooking model
class YogaBookingSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = YogaBooking
        # Exclude certain fields from serialization
        exclude = ("id", "created_at")
        # Set certain fields as read-only
        read_only_fields = ("external_id", "created_at",)
    
    # Custom validation for date_of_birth field
    def validate_date_of_birth(self, value):
        today = datetime.date.today()
        # Check if the user is 18 years or older
        if (today.year - value.year) < 18:
            raise serializers.ValidationError("You must be 18 years or older to book a yoga class")
        # Check if the user is 65 years or younger
        if (today.year - value.year) > 65:
            raise serializers.ValidationError("You must be 65 years or younger to book a yoga class")
        return value
    
    # Custom create method to handle additional logic on object creation
    def create(self, validated_data):
        # Extract data from the initial request data
        offer = self.initial_data.get("coupon_code", None)
        yoga_timing = self.initial_data.get("yoga_timing")
        
        # Get or create a YogaBooking instance
        yoga_booking, _ = YogaBooking.objects.get_or_create(**validated_data)
        
        # Calculate the amount (default is 500 INR)
        amount = 500
        offer_instance = None
        
        # Apply discount from the offer, if provided
        if offer:
            offer_instance = Offer.objects.get(code=offer)
            amount -= offer_instance.discount
        
        # Set currency and status for the Order
        currency = "INR"
        status = "created"
        
        # Get the YogaTimings instance
        yoga_timing = YogaTimings.objects.get(external_id=yoga_timing)
        
        # Create an Order instance with relevant details
        if offer_instance:
            Order.objects.create(amount=amount, currency=currency, status=status, 
                                 yoga_booking=yoga_booking, yoga_batch=yoga_timing.batch, 
                                 yoga_timing=yoga_timing, offer=offer_instance)
        else:
            Order.objects.create(amount=amount, currency=currency, status=status, 
                                 yoga_booking=yoga_booking, yoga_batch=yoga_timing.batch, 
                                 yoga_timing=yoga_timing)
        
        return yoga_booking
    
    # Customize the representation of the serialized data
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Add order information to the serialized data
        data["order"] = instance.order.last().external_id
        data["proceed_to_pay"] = instance.order.last().amount
        data.pop("yoga_batch")  # Remove yoga_batch field from the output
        return data

# Serializer for handling nested YogaTimings within YogaBatch
class NestedYogaBatchTimingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = YogaTimings
        # Exclude certain fields from serialization
        exclude = ("id", "timespan", "batch")
        # Set certain fields as read-only
        read_only_fields = ("external_id", "created_at",)

# Serializer for handling YogaBatch model
class YogaBatchSerializer(serializers.ModelSerializer):
    # Include nested YogaTimings serializer for timings field
    timings = NestedYogaBatchTimingsSerializer(many=True)
    class Meta:
        model = YogaBatch
        # Exclude certain fields from serialization
        exclude = ("id", "created_at")
        # Set certain fields as read-only
        read_only_fields = ("external_id", "created_at",)
from django.db import models
import uuid
from django.db import models
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DateTimeRangeField
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import pytz

MONTHS = {
        1: 'January',
        2: 'February',
        3: 'March',
        4: 'April',
        5: 'May',
        6: 'June',
        7: 'July',
        8: 'August',
        9: 'September',
        10: 'October',
        11: 'November',
        12: 'December',
    }

class YogaTimings(models.Model):
    external_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    timespan = DateTimeRangeField()
    batch = models.ForeignKey('YogaBatch', on_delete=models.CASCADE, related_name='timings', blank=True, null=True)

    class Meta:
        constraints = [
            ExclusionConstraint(
                name='exclude_overlapping_timings',
                expressions=[
                    ('timespan', '&&'),
                ],
            ),
        ]

    def save(self, *args, **kwargs):
        self.start_time = self.start_time.replace(day=1)
        self.end_time = self.end_time.replace(day=1)
        self.timespan = (self.start_time, self.end_time)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.start_time} - {self.end_time}'



class YogaBatch(models.Model):
    MONTH_CHOICES = [
        (1, 'January'),
        (2, 'February'),
        (3, 'March'),
        (4, 'April'),
        (5, 'May'),
        (6, 'June'),
        (7, 'July'),
        (8, 'August'),
        (9, 'September'),
        (10, 'October'),
        (11, 'November'),
        (12, 'December'),
    ]
    external_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    year = models.IntegerField()
    month = models.IntegerField(choices=MONTH_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'yoga_batch'
        unique_together = ('year', 'month',)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.year} - {MONTHS[self.month]}'

class YogaBooking(models.Model):
    external_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=250)
    email = models.EmailField(max_length=250)
    date_of_birth = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    yoga_batch = models.ForeignKey(YogaBatch, on_delete=models.CASCADE, related_name='yoga_users', blank=True, null=True)

    @property
    def is_paid(self):
        return self.order.filter(status='paid').exists()
    class Meta:
        db_table = 'yoga_user'
        indexes = [
            models.Index(fields=['email',]),
        ]

    def __str__(self):
        return self.name
    
class Offer(models.Model):
    external_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=30)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    validity_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=30, unique=True)

    class Meta:
        db_table = 'offer'

    def __str__(self):
        return self.name

class Order(models.Model):
    ORDER_STATUS = (
        ('created', 'created'),
        ('paid', 'paid'),
        ('cancelled', 'cancelled'),
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    external_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=30, default='created', choices=ORDER_STATUS)
    yoga_booking = models.ForeignKey(YogaBooking, on_delete=models.CASCADE, related_name='order')
    yoga_batch = models.ForeignKey(YogaBatch, on_delete=models.CASCADE, related_name='order')
    yoga_timing = models.ForeignKey(YogaTimings, on_delete=models.CASCADE, related_name='order')
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='order', blank=True, null=True)
    class Meta:
        db_table = 'order'

@receiver(post_save, sender=YogaBatch)
def create_default_timings(sender, instance, created, **kwargs):
    if created:
        timings = [
            YogaTimings(start_time=timezone.datetime(instance.year, instance.month, 1, 6, tzinfo=pytz.UTC), end_time=timezone.datetime(instance.year, instance.month, 1, 7, tzinfo=pytz.UTC)),
            YogaTimings(start_time=timezone.datetime(instance.year, instance.month, 1, 7, tzinfo=pytz.UTC), end_time=timezone.datetime(instance.year, instance.month, 1, 8, tzinfo=pytz.UTC)),
            YogaTimings(start_time=timezone.datetime(instance.year, instance.month, 1, 8, tzinfo=pytz.UTC), end_time=timezone.datetime(instance.year, instance.month, 1, 9, tzinfo=pytz.UTC)),
            YogaTimings(start_time=timezone.datetime(instance.year, instance.month, 1, 17, tzinfo=pytz.UTC), end_time=timezone.datetime(instance.year, instance.month, 1, 18, tzinfo=pytz.UTC)),
        ]
        for timing in timings:
            timing.save()
            instance.timings.add(timing)
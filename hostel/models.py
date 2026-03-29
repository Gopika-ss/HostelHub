from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
import calendar
from datetime import date
def get_month_end():
    today = date.today()
    last_day = calendar.monthrange(today.year, today.month)[1]
    return today.replace(day=last_day)
# ---------------- STUDENT PROFILE ----------------
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=100)
    register_no = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100)
    year = models.CharField(max_length=20)
    # ROOM PREFERENCE
    ROOM_PREFERENCE_CHOICES = (
        ('2 Sharing', '2 Sharing'),
        ('4 Sharing', '4 Sharing'),
        ('6 Sharing', '6 Sharing'),
    )
    room_preference = models.CharField(
        max_length=20,
        choices=ROOM_PREFERENCE_CHOICES,
        blank=True,
        null=True
    )
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    parent_name = models.CharField(max_length=100, blank=True)
    parent_phone = models.CharField(max_length=15, blank=True)
    def __str__(self):
        return f"{self.register_no} - {self.full_name}"
# ---------------- ROOM ----------------
class Room(models.Model):
    ROOM_TYPE_CHOICES = (
        ('2 Sharing', '2 Sharing'),
        ('4 Sharing', '4 Sharing'),
        ('6 Sharing', '6 Sharing'),
    )
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(
        max_length=20,
        choices=ROOM_TYPE_CHOICES,
        default='2 Sharing'
    )
    capacity = models.PositiveIntegerField()
    floor = models.PositiveIntegerField(default=1)
    block = models.CharField(max_length=50, default="A")
    @property
    def is_available(self):
        return self.allocations.count() < self.capacity
    def __str__(self):
        return f"Room {self.room_number} ({self.room_type})"   
class Fee(models.Model):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="fees"
    )
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    paid = models.BooleanField(default=False)
    paid_on = models.DateTimeField(null=True, blank=True)
    due_date = models.DateField(default=get_month_end)
    def __str__(self):
        status = "Paid" if self.paid else "Pending"
        return f"{self.student.full_name} - {status}"
# ---------------- ALLOCATION ----------------
class Allocation(models.Model):
    student = models.OneToOneField(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="allocation"
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="allocations"
    )
    allocated_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.student.full_name} → {self.room.room_number}"

    # 🔥 VALIDATION (PREVENT OVER-ALLOCATION)
    def clean(self):
        # exclude current instance (important when editing)
        current_count = self.room.allocations.exclude(id=self.id).count()

        if current_count >= self.room.capacity:
            raise ValidationError("This room is already full!")

    def save(self, *args, **kwargs):
        self.full_clean()   # 🔥 MUST CALL VALIDATION
        super().save(*args, **kwargs)

        # Fee generation
        if self.room.room_type == '2 Sharing':
            amount = 4000
        elif self.room.room_type == '4 Sharing':
            amount = 2500
        else:
            amount = 2000

        today = date.today()
        last_day = calendar.monthrange(today.year, today.month)[1]
        due_date = today.replace(day=last_day)

        Fee.objects.update_or_create(
            student=self.student,
            due_date=due_date,
            defaults={
                'amount': amount,
                'paid': False
            }
        )
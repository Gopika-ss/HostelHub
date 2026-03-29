from django.contrib import admin
from .models import Room, StudentProfile, Allocation, Fee
# ---------------- ROOM ADMIN ----------------
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = (
        'room_number',
        'capacity',
        'occupied_beds',
        'available_beds',
    )

    search_fields = ('room_number',)

    def occupied_beds(self, obj):
        return obj.allocations.count()
    occupied_beds.short_description = "Occupied Beds"

    def available_beds(self, obj):
        return obj.capacity - obj.allocations.count()
    available_beds.short_description = "Available Beds"

# ---------------- STUDENT PROFILE ADMIN ----------------
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'full_name',
        'register_no',
        'department',
        'year',
        'room_preference', 
        'room_number'
    )
    readonly_fields=('room_preference',)
    def room_number(self, obj):
        allocation = Allocation.objects.filter(student=obj).first()
        if allocation:
            return allocation.room.room_number
        return "Not Allocated"

    room_number.short_description = "Room"

    search_fields = ('user__username', 'register_no')

    list_filter = (
        'department',
        'year',
        'room_preference'   
    )
@admin.register(Allocation)
class AllocationAdmin(admin.ModelAdmin):
    search_fields = ('student__register_no', 'student__full_name')
    list_display = ('student', 'room', 'allocated_date')
    list_filter = ('room',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "student":
            from .models import StudentProfile, Allocation

            allocated_students = Allocation.objects.values_list('student_id', flat=True)

            kwargs["queryset"] = StudentProfile.objects.exclude(id__in=allocated_students)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)
# ---------------- FEE ADMIN ----------------
@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount', 'paid','paid_on','due_date')
    list_filter = ('paid',)
admin.site.site_header = "Hostel Room Manager Admin"
admin.site.site_title = "Hostel Admin Portal"
admin.site.index_title = "Welcome to Room Manager"
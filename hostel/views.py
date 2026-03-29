from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Room, StudentProfile, Allocation, Fee
import calendar
from datetime import date

def get_student_profile(user):
    return StudentProfile.objects.filter(user=user).first()
def about(request):
    return render(request, 'hostel/about.html')
def get_month_end():
    today = date.today()
    last_day = calendar.monthrange(today.year, today.month)[1]
    return date(today.year, today.month, last_day)
# ---------------- HOME ----------------
def index(request):
    return render(request, 'hostel/index.html')
def room_types(request):
    return render(request, 'hostel/room_types.html')
def contact(request):
    return render(request, 'hostel/contact.html')
# ---------------- STUDENT LOGIN ----------------
def student_login(request):
    logout(request)  
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            if user.is_staff:
                return redirect('/admin/')  
            else:
                login(request, user)
                return redirect('student_dashboard')
        return render(request, 'hostel/student_login.html', {
            'error': 'Invalid username or password'
        })
    return render(request, 'hostel/student_login.html')
# ---------------- STUDENT REGISTER ----------------
def student_register(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('/admin/')
        return redirect('student_dashboard')

    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        full_name = request.POST.get('full_name')
        register_no = request.POST.get('register_no')
        department = request.POST.get('department')
        year = request.POST.get('year')
        password = request.POST.get('password')

        # check username
        if User.objects.filter(username=username).exists():
            return render(request, 'hostel/student_register.html', {
                'error': 'Username already exists'
            })

        # check register number uniqueness
        if StudentProfile.objects.filter(register_no=register_no).exists():
            return render(request, 'hostel/student_register.html', {
                'error': 'Register Number already exists'
            })

        # create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # create student profile directly ✅
        StudentProfile.objects.create(
            user=user,
            full_name=full_name,
            register_no=register_no,
            department=department,
            year=year
        )

        messages.success(request, "Registration successful. Please login.")
        return redirect('student_login')

    return render(request, 'hostel/student_register.html')
# ---------------- LOGOUT ----------------
def student_logout(request):
    logout(request)
    return redirect('index')
# ---------------- STUDENT DASHBOARD ----------------
@login_required
def student_dashboard(request):
    if request.user.is_staff:
        return redirect('/admin/')
    profile = get_student_profile(request.user)
    if not profile:
        return redirect('student_login')
    allocation = Allocation.objects.filter(student=profile).select_related('room').first()
    return render(request, 'hostel/student_dashboard.html', {
        'profile': profile,
        'allocation': allocation
    })
# ---------------- FACILITIES ----------------
def facilities(request):
    return render(request, 'hostel/facilities.html')
# ---------------- MY ROOM ----------------
@login_required
def my_room(request):
    if request.user.is_staff:
        return redirect('/admin/')
    profile = get_student_profile(request.user)
    if not profile:
        return redirect('student_login')
    allocation = Allocation.objects.filter(student=profile).select_related('room').first()
    if allocation:
        room = allocation.room
        room.occupied_count = Allocation.objects.filter(room=room).count()
    return render(request, 'hostel/my_room.html', {
        'allocation': allocation
    })
# ---------------- RENT STATUS ----------------
@login_required
def rent_status(request):
    if request.user.is_staff:
        return redirect('/admin/')
    profile=get_student_profile(request.user)
    if not profile:
        return redirect('student_login')
    allocation=Allocation.objects.filter(student=profile).first()
    if not allocation:
        return render(request,'hostel/rent_status.html',{
            'no_room':True,
            'today':date.today(),
        })
    fee=Fee.objects.filter(student=profile,due_date=get_month_end()).first()
    if not fee:
        if allocation.room.room_type=='2 Sharing':
            amount=4000
        elif allocation.room.room_type=='4 Sharing':
            amount=2500
        else:
            amount=2000
        Fee.objects.create(
            student=profile,
            amount=amount,
            due_date=get_month_end(),
            paid=False
        )
    fees=Fee.objects.filter(student=profile).order_by('-due_date')
    return render(request,'hostel/rent_status.html',{
        'fees':fees,
        'today':date.today(),
    })
@login_required
def allocate_room(request,room_id):
    if request.user.is_staff:
        return redirect('/admin/')
    profile=get_student_profile(request.user)
    if not profile:
        return redirect('student_login')
    if Allocation.objects.filter(student=profile).exists():
        messages.warning(request,"Room already allocated!")
        return redirect('student_dashboard')
    room=Room.objects.filter(id=room_id).first()
    if not room:
        messages.error(request,"Room not found.")
        return redirect('student_dashboard')
    if Allocation.objects.filter(room=room).count()>=room.capacity:
        messages.error(request,"Room Full!")
        return redirect('student_dashboard')
    Allocation.objects.create(student=profile,room=room)
    messages.success(request,"Room Allocated Successfully! Rent Generated.")
    return redirect('student_dashboard')
# ---------------- ALLOCATE ROOM ----------------
@login_required
def allocate_room(request, room_id):
    if request.user.is_staff:
        return redirect('/admin/')
    profile = get_student_profile(request.user)
    if not profile:
        return redirect('student_login')
    if Allocation.objects.filter(student=profile).exists():
        messages.warning(request, "Room already allocated!")
        return redirect('student_dashboard')
    room = Room.objects.filter(id=room_id).first()
    if not room:
        messages.error(request, "Room not found.")
        return redirect('student_dashboard')
    if Allocation.objects.filter(room=room).count() >= room.capacity:
        messages.error(request, "Room Full!")
        return redirect('student_dashboard')
    Allocation.objects.create(
        student=profile,
        room=room
    )
    Fee.objects.create(
        student=profile,
        amount=5000,
        due_date=get_month_end(),
        paid=False
    )
    messages.success(request, "Room Allocated Successfully! Rent Generated.")
    return redirect('student_dashboard')
# ---------------- ROOM PREFERENCE ----------------
@login_required
def room_preference(request):
    if request.user.is_staff:
        return redirect('/admin/')

    profile = get_student_profile(request.user)
    if not profile:
        return redirect('student_login')

    if request.method == "POST":
        pref = request.POST.get('room_preference')
        profile.room_preference = pref
        profile.save()
        return redirect('student_dashboard')

    rooms = Room.objects.all()

    for room in rooms:
        room.occupied = Allocation.objects.filter(room=room).count()
        room.available = room.capacity - room.occupied

    return render(request, 'hostel/room_preference.html', {
        'profile': profile,
        'rooms': rooms
    })
# ---------------- STUDENT PROFILE ----------------
@login_required
def student_profile(request):
    if request.user.is_staff:
        return redirect('/admin/')
    profile = get_student_profile(request.user)
    if not profile:
        return redirect('student_login')
    allocation = Allocation.objects.filter(student=profile).first()
    if request.method == "POST":
        profile.full_name = request.POST.get("full_name")
        profile.register_no = request.POST.get("register_no")
        profile.department = request.POST.get("department")
        profile.year = request.POST.get("year")
        profile.phone = request.POST.get("phone")
        profile.address = request.POST.get("address")
        profile.parent_name = request.POST.get("parent_name")
        profile.parent_phone = request.POST.get("parent_phone")
        email = request.POST.get("email")
        if email:
            request.user.email = email
            request.user.save()
        profile.save()
        messages.success(request, "Profile Updated Successfully!")
        return redirect("student_profile")
    return render(request, "hostel/student_profile.html", {
        "profile": profile,
        "allocation": allocation
    })


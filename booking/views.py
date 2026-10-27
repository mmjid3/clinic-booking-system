from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import AppointmentForm, UserProfileForm, ReviewForm, CustomUserCreationForm
from .models import Service, Staff, Appointment, Review
from datetime import timedelta, datetime
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import logout, login
from django.db.models import Avg
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib.auth.models import User

def home(request):
    services = Service.objects.all()
    specialty_filter = request.GET.get('specialty')

    if specialty_filter:
        staff_members = Staff.objects.filter(specialty=specialty_filter)
    else:
        staff_members = Staff.objects.all()

    return render(request, 'booking/home.html', {'services': services, 'staff_members': staff_members})


def doctor_detail(request, pk):
    doctor = get_object_or_404(Staff, pk=pk)
    reviews = doctor.reviews.all().order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    return render(request, 'booking/doctor_detail.html', {
        'doctor': doctor,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'total_reviews': reviews.count()
    })


@login_required
@xframe_options_exempt
def book_appointment(request):
    doctor_id = request.GET.get('doctor_id')
    if not doctor_id:
        return redirect('home')

    doctor = get_object_or_404(Staff, pk=doctor_id)
    selected_date_str = request.GET.get('date')

    # لیست روزهای کاری ۷ روز آینده
    available_days = []
    today = timezone.now().date()
    for i in range(1, 8):
        day = today + timedelta(days=i)
        available_days.append({
            'date': day,
            'label': day.strftime('%A, %b %d')
        })

    available_slots = []

    if selected_date_str:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        service = doctor.services.first()

        if service:
            start_dt = timezone.make_aware(datetime.combine(selected_date, doctor.work_start_time))
            end_dt = timezone.make_aware(datetime.combine(selected_date, doctor.work_end_time))
            duration = timedelta(minutes=service.duration)

            existing_appts = Appointment.objects.filter(
                staff=doctor,
                start_time__date=selected_date
            ).exclude(status='cancelled')

            current_time = start_dt
            while current_time + duration <= end_dt:
                slot_end = current_time + duration
                is_booked = False

                for appt in existing_appts:
                    if (current_time < appt.end_time) and (slot_end > appt.start_time):
                        is_booked = True
                        break

                available_slots.append({
                    'start': current_time,
                    'is_booked': is_booked,
                    'label': current_time.strftime('%H:%M'),
                    'service_id': service.id
                })

                current_time = slot_end

    if request.method == 'POST' and 'confirm_booking' in request.POST:
        selected_start_str = request.POST.get('selected_start_time')
        service_id = request.POST.get('service_id')

        if selected_start_str and service_id:
            service = get_object_or_404(Service, pk=service_id)
            selected_start_dt = timezone.datetime.fromisoformat(selected_start_str)

            appointment = Appointment(
                customer=request.user,
                staff=doctor,
                service=service,
                start_time=selected_start_dt,
                end_time=selected_start_dt + timedelta(minutes=service.duration)
            )
            appointment.save()
            return redirect('booking_success', pk=appointment.pk)

    return render(request, 'booking/book.html', {
        'doctor': doctor,
        'available_days': available_days,
        'slots': available_slots,
        'selected_date': selected_date_str
    })


@login_required
def booking_success(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk, customer=request.user)
    return render(request, 'booking/success.html', {'appointment': appointment})


@login_required
def user_dashboard(request):
    recent_appointments = Appointment.objects.filter(customer=request.user).order_by('-start_time')[:3]
    profile_form = UserProfileForm(instance=request.user)

    return render(request, 'booking/dashboard.html', {
        'recent_appointments': recent_appointments,
        'user': request.user,
        'form': profile_form
    })


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('user_dashboard')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'booking/edit_profile.html', {'form': form})


@login_required
def my_appointments(request):
    appointments = Appointment.objects.filter(customer=request.user).order_by('-start_time')
    return render(request, 'booking/my_appointments.html', {'appointments': appointments})


@login_required
def cancel_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk, customer=request.user)

    if appointment.status in ['pending', 'confirmed']:
        appointment.status = 'cancelled'
        appointment.save()
        messages.success(request, "Appointment cancelled successfully.")
    else:
        messages.error(request, "This appointment cannot be cancelled.")

    return redirect('my_appointments')


@login_required
def add_review(request, appointment_pk):
    appointment = get_object_or_404(Appointment, pk=appointment_pk, customer=request.user)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.doctor = appointment.staff
            review.patient = request.user
            review.save()

            appointment.status = 'completed'
            appointment.save()

            messages.success(request, "Thank you! Your review has been submitted.")
            return redirect('doctor_detail', pk=appointment.staff.pk)
    else:
        form = ReviewForm()

    return render(request, 'booking/add_review.html', {'form': form, 'appointment': appointment})


def custom_logout(request):
    logout(request)
    return redirect('home')


def services_list(request):
    services = Service.objects.all().order_by('category')
    return render(request, 'booking/services.html', {'services': services})


@login_required
def add_doctor_review(request, doctor_pk):
    doctor = get_object_or_404(Staff, pk=doctor_pk)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if rating and comment:
            Review.objects.create(
                doctor=doctor,
                patient=request.user,
                rating=int(rating),
                comment=comment
            )
            messages.success(request, "Your review has been submitted successfully.")
            return redirect('doctor_detail', pk=doctor.pk)

    return redirect('doctor_detail', pk=doctor.pk)


@login_required
def my_reviews(request):
    reviews = Review.objects.filter(patient=request.user).order_by('-created_at')
    return render(request, 'booking/my_reviews.html', {'reviews': reviews})


@login_required
def edit_review(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk, patient=request.user)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if rating and comment:
            review.rating = int(rating)
            review.comment = comment
            review.save()
            messages.success(request, "Your review has been updated.")
            return redirect('my_reviews')

    return render(request, 'booking/edit_review.html', {'review': review})


@login_required
def delete_review(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk, patient=request.user)

    if request.method == 'POST':
        review.delete()
        messages.success(request, "Your review has been deleted.")
        return redirect('my_reviews')

    return render(request, 'booking/delete_review.html', {'review': review})


def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your account has been created successfully!")
            return redirect('user_dashboard')
    else:
        form = CustomUserCreationForm()

    # استایل بوت استرپ
    for field in form.fields.values():
        if field.widget.attrs.get('class') is None:
            field.widget.attrs.update({'class': 'form-control form-control-lg'})

    return render(request, 'registration/signup.html', {'form': form})

from django.db import models
from django.contrib.auth.models import User


class Service(models.Model):
    name = models.CharField(max_length=100, verbose_name="Service Name")
    category = models.CharField(max_length=100, default="General", verbose_name="Category")  # فیلد جدید
    duration = models.PositiveIntegerField(help_text="Duration in minutes", verbose_name="Duration (min)")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price")

    def __str__(self):
        return f"{self.name} ({self.duration} min)"

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"


class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="User Account")
    name = models.CharField(max_length=100, verbose_name="Full Name")
    specialty = models.CharField(max_length=150, default="General Practitioner", verbose_name="Specialty")
    medical_code = models.CharField(max_length=20, blank=True, null=True, verbose_name="Medical Council Code")
    bio = models.TextField(blank=True, null=True, verbose_name="Biography")
    address = models.CharField(max_length=255, default="Main Clinic, City Center", verbose_name="Clinic Address")
    image_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="Profile Image URL")  # فیلد جدید
    services = models.ManyToManyField(Service, verbose_name="Provided Services")
    work_start_time = models.TimeField(default='09:00', verbose_name="Work Start Time")
    work_end_time = models.TimeField(default='17:00', verbose_name="Work End Time")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Staff / Doctor"
        verbose_name_plural = "Staff / Doctors"


class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_appointments',
                                 verbose_name="Patient / Customer")
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='staff_appointments', verbose_name="Doctor")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name="Service")

    start_time = models.DateTimeField(verbose_name="Start Time")
    end_time = models.DateTimeField(verbose_name="End Time")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Status")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    def __str__(self):
        return f"{self.customer.username} - {self.staff.name} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"


class Review(models.Model):
    doctor = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='reviews', verbose_name="Doctor")
    patient = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Patient")
    rating = models.PositiveSmallIntegerField(default=5, verbose_name="Rating (1-5)")
    comment = models.TextField(verbose_name="Comment")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    def __str__(self):
        return f"{self.patient.username} -> {self.doctor.name} ({self.rating} stars)"

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from booking.models import Service, Staff, Appointment, Review
from datetime import timedelta, datetime
from django.utils import timezone
import random


class Command(BaseCommand):
    help = 'Seeds the database with 100 doctors and 100 users'

    def handle(self, *args, **kwargs):
        self.stdout.write("Clearing old data...")
        Appointment.objects.all().delete()
        Review.objects.all().delete()
        Staff.objects.all().delete()
        Service.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write("Creating Services & Categories...")
        categories = ["Cardiology", "Dermatology", "Dentistry", "Neurology", "Pediatrics", "Orthopedics", "General"]
        services_data = [
            ("General Consultation", "General", 15, 50),
            ("Dental Checkup", "Dentistry", 30, 80),
            ("Dermatology Consultation", "Dermatology", 20, 100),
            ("Cardiology Screening", "Cardiology", 45, 150),
            ("Pediatric Checkup", "Pediatrics", 20, 70),
            ("Brain Scan (MRI)", "Neurology", 60, 200),
            ("Bone Fracture Check", "Orthopedics", 30, 120),
            ("Skin Biopsy", "Dermatology", 25, 90),
        ]

        services = []
        for name, cat, dur, price in services_data:
            s = Service.objects.create(name=name, category=cat, duration=dur, price=price)
            services.append(s)

        self.stdout.write("Creating 100 Doctors...")
        first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William",
                       "Elizabeth"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez",
                      "Martinez"]
        specialties = categories

        doctors = []
        for i in range(100):
            fn = random.choice(first_names)
            ln = random.choice(last_names)
            username = f"dr_{fn.lower()}_{ln.lower()}_{i}"

            user = User.objects.create_user(username=username, password='password123', first_name=fn, last_name=ln)

            # استفاده از سرویس randomuser.me برای عکس‌های واقعی
            img_url = f"https://randomuser.me/api/portraits/{'women' if i % 2 == 0 else 'men'}/{i % 99}.jpg"

            doctor = Staff.objects.create(
                user=user,
                name=f"Dr. {fn} {ln}",
                specialty=random.choice(specialties),
                medical_code=f"MC-{10000 + i}",
                address=f"{random.randint(1, 200)} Medical St, City {random.randint(1, 10)}",
                bio=f"Experienced specialist in {random.choice(specialties)} with over {random.randint(5, 30)} years of practice. Dedicated to providing the best care.",
                image_url=img_url
            )

            # اختصاص دادن ۲ تا ۴ سرویس به هر دکتر
            assigned_services = random.sample(services, k=random.randint(2, 4))
            doctor.services.add(*assigned_services)
            doctors.append(doctor)

        self.stdout.write("Creating 100 Patients...")
        patients = []
        for i in range(100):
            fn = random.choice(first_names)
            ln = random.choice(last_names)
            username = f"patient_{fn.lower()}_{ln.lower()}_{i}"
            user = User.objects.create_user(username=username, password='password123', first_name=fn, last_name=ln,
                                            email=f"{username}@example.com")
            patients.append(user)

        self.stdout.write("Creating Reviews...")
        comments = [
            "Excellent doctor! Very professional and caring.",
            "The appointment was on time and the staff was friendly.",
            "Good experience overall, but the waiting room was crowded.",
            "Highly recommend. The doctor explained everything clearly.",
            "Very knowledgeable and patient. Answered all my questions.",
            "The clinic was clean and modern. Doctor was helpful.",
            "It was okay. Nothing special but got the job done.",
            "Amazing doctor! Made me feel very comfortable.",
            "The doctor was a bit rushed, but the treatment worked.",
            "Best specialist I've visited in years!"
        ]

        for _ in range(500):  # ساخت 500 نظر رندوم
            doctor = random.choice(doctors)
            patient = random.choice(patients)
            rating = random.randint(3, 5)  # اکثرا امتیاز بالا
            comment = random.choice(comments)

            Review.objects.create(
                doctor=doctor,
                patient=patient,
                rating=rating,
                comment=comment
            )

        self.stdout.write(self.style.SUCCESS("Successfully generated 100 Doctors, 100 Users, and 500 Reviews!"))
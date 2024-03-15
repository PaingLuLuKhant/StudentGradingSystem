from django.db.models.signals import post_save , post_delete
from django.dispatch import receiver
from .models import Enrollment, SGPA, Student
from .views import calculate_sgpa, calculate_cgpa

@receiver(post_save, sender=Enrollment)
def update_sgpa_and_cgpa(sender, instance, created, **kwargs):
    roll_number = instance.roll_number
    sem_id = instance.sem_id
    sgpa, created = SGPA.objects.get_or_create(roll_number=roll_number, sem_id=sem_id)
    if created or kwargs.get('update_fields', None) != 'grade':
        # New SGPA record created or grade field updated, calculate and save the SGPA
        sgpa.value = calculate_sgpa(roll_number, sem_id)
        sgpa.save()

    cgpa = calculate_cgpa(roll_number)
    try:
        student = Student.objects.get(roll_number=roll_number)
        student.cgpa = cgpa
        student.save()
    except Student.DoesNotExist:
        print(f"No Student found with roll_number {roll_number}")


@receiver(post_delete, sender=Enrollment)
def update_sgpa_and_cgpa_on_grade_deletion(sender, instance, **kwargs):
    roll_number = instance.roll_number
    sem_id = instance.sem_id

    # Check if there are any remaining enrollments for the semester
    remaining_enrollments = Enrollment.objects.filter(roll_number=roll_number, sem_id=sem_id)
    if remaining_enrollments.exists():
        # Recalculate SGPA for the semester
        sgpa, created = SGPA.objects.get_or_create(roll_number=roll_number, sem_id=sem_id)
        sgpa.value = calculate_sgpa(roll_number, sem_id)
        sgpa.save()
    else:
        SGPA.objects.filter(roll_number=roll_number, sem_id=sem_id).delete()

    cgpa = calculate_cgpa(roll_number)
    try:
        student = Student.objects.get(roll_number=roll_number)
        student.cgpa = cgpa
        student.save()
    except Student.DoesNotExist:
        print(f"No Student found with roll_number {roll_number}")
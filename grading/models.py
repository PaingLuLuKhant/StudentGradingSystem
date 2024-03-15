from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

class Student(models.Model):
    roll_number = models.CharField(primary_key=True, max_length=20)
    name = models.CharField(max_length=100, default='')
    cgpa = models.FloatField(default=0.0)

    def get_batch(self):
        return self.roll_number.split('-')[0]
    
    def __str__(self):
        return self.roll_number
    
    def admin_display(self):
        return f"{self.roll_number} - {self.name} - {self.cgpa}"

class Semester(models.Model):
    sem_id = models.CharField(primary_key=True, max_length=20)
    semester_name = models.CharField(max_length=20, default='I Semester')

    def __str__(self):
        return self.semester_name

class Course(models.Model):
    course_code = models.CharField(primary_key=True, max_length=10)
    course_name = models.CharField(max_length=100, default='')
    credits = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.course_code} - {self.course_name} - {self.credits} credits"

class Enrollment(models.Model):
    enrollment_id = models.AutoField(primary_key=True)
    roll_number = models.ForeignKey(Student, on_delete=models.CASCADE)
    course_code = models.ForeignKey(Course, on_delete=models.CASCADE)
    sem_id = models.ForeignKey(Semester, on_delete=models.CASCADE)
    grade = models.CharField(max_length=2, validators=[RegexValidator(regex='^(A|A-|B\\+|B|B-|C\\+|C|D|F|RC)$')])
    
    def clean(self):
        super().clean()
        if self.grade not in ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'D', 'F', 'RC']:
            raise ValidationError({'grade': 'Invalid grade value'})
        
    class Meta:
        unique_together = ('roll_number', 'course_code', 'sem_id')
        
    def __str__(self):
        return f"{self.roll_number} -- {self.course_code.course_code} -- {self.sem_id} -- {self.grade}"

class SGPA(models.Model):
    sem_id = models.ForeignKey(Semester, on_delete=models.CASCADE)
    roll_number = models.ForeignKey(Student, on_delete=models.CASCADE)
    value = models.FloatField(default=0.0)
    
    class Meta:
        unique_together = ('roll_number', 'sem_id')
    
    def __str__(self):
        return f"{self.roll_number} - {self.sem_id} - {self.value}"


from django.contrib import admin
from .models import Student, Course, Semester, Enrollment ,SGPA
from django.forms import inlineformset_factory
from django.db.models.functions import Substr
from django.db.models import IntegerField


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0  # To show existing enrollments without additional empty rows
    readonly_fields = ['course_code', 'sem_id', 'grade']  # Make fields read-only
    ordering = ['sem_id__sem_id']
    can_delete = False

class StudentAdmin(admin.ModelAdmin):
    inlines = [EnrollmentInline]
    
     # Add a method to display the Student instances in the admin interface
    def admin_display(self, obj):
        return obj.admin_display()
    admin_display.short_description = 'Student'

    # Use the admin_display method in the list_display
    list_display = ('admin_display',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(batch=Substr('roll_number',  1,  4)).order_by('batch', 'roll_number')
        return qs


admin.site.register(Student, StudentAdmin)
admin.site.register(Semester)
admin.site.register(Course)
admin.site.register(Enrollment)
admin.site.register(SGPA)





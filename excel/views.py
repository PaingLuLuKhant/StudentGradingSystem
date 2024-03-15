#views.py
from django.http import HttpResponse
from django.shortcuts import render
from grading.models import Student,Course,Enrollment,SGPA,Semester
import pandas as pd
from io import BytesIO
from django.http import JsonResponse
from django.core.files.storage import default_storage

import logging

# Configure the logging module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger object
logger = logging.getLogger(__name__)

'''
def upload_excel(request):
     if request.method == 'POST':
        contexts = []
        updated_text = []
        excel_file = request.FILES['excel_file']
        upload_type = request.POST.get('upload_type', '')
        temp_path = default_storage.save('temp/' + excel_file.name, excel_file)
        df = pd.read_excel(default_storage.path(temp_path))
        def remove_duplicates(contexts):
             return list(set(contexts))

        try:
            #Assuming the first row contains headers and the rest contain data
            print(upload_type)
            if upload_type == 'students':
                error = 0
                success = 0
                for _, row in df.iterrows():
                    student = Student.objects.filter(roll_number=row['Roll Number']).first()
                    if not student:
                        instance = Student(roll_number=row['Roll Number'], name=row['Name'])
                        instance.save()
                        success+=1
                    else:
                        contexts.append(f'{row["Roll Number"]} - {row["Name"]}')
                        error+=1
                updated_text.append(f'Database is updated for {success} rows and {error} rows were skipped')

            elif upload_type == 'courses':
                error=0
                success=0
                for _, row in df.iterrows():
                    course = Course.objects.filter(course_code=row['Course Code']).first()
                    if not course:
                        instance = Course(course_code=row['Course Code'], course_name=row['Course Name'], credits=row['Credits'])
                        instance.save()
                        success+=1
                    else:
                        contexts.append(f'{row["Course Code"]} - {row["Course Name"]} ')
                        error +=1
                updated_text.append(f'Database is updated for {success} rows and {error} rows were skipped')

            elif upload_type == 'enrollment':
                print("hello")
                error=0
                success=0
                for index, row in df.iterrows():
                    student = Student.objects.filter(roll_number=row['Roll Number']).first()
                    semester = Semester.objects.filter(sem_id=row['Semester']).first()
                    course = Course.objects.filter(course_code=row['Course Code']).first()
                     
                    enrollment = Enrollment.objects.filter(roll_number=student, sem_id=semester, course_code=course)
                    if not student:
                        print("1")
                        contexts.append(f'{row["Roll Number"]} does not exist.')
                        error+=1
                        continue
                    
                    if not semester:
                        print("2")
                        contexts.append(f'{row["Semester"]} does not exist.')
                        error+=1
                        continue
                    
                    if not course:
                        print("3")
                        contexts.append(f'{row["Course Code"]} does not exist.')
                        error+=1   
                        continue                    
                    
                    if enrollment:
                        print("4")
                        contexts.append(f'{row["Roll Number"]}, {row["Semester"]}, {row["Course Code"]}, {row["Grade"]}')
                        error+=1
                        continue
                    else:
                        print("5")
                        instance = Enrollment(roll_number=student, sem_id=semester, course_code=course, grade=row['Grade'])
                        instance.save()  
                        success+=1     
                updated_text.append(f'Database is updated for {success} rows and {error} rows were skipped')

            else:
                return JsonResponse({'message': 'Invalid upload type.'})   
        finally:
            default_storage.delete(temp_path)
            contexts = remove_duplicates(contexts)
            return JsonResponse({
                'message': 'An excel file is received.',
                'updated_text' : updated_text,
                'context': contexts, 
            })
     else:
         return JsonResponse({'error': 'Invalid request'}, status=400)
    '''
    
def upload_excel(request):
     if request.method == 'POST':
        contexts = []
        excel_file = request.FILES['excel_file']
        upload_type = request.POST.get('upload_type', '')
        temp_path = default_storage.save('temp/' + excel_file.name, excel_file)
        df = pd.read_excel(default_storage.path(temp_path))
        def remove_duplicates(contexts):
             return list(set(contexts))

        try:
            #Assuming the first row contains headers and the rest contain data
            if upload_type == 'semesters':
                 error = 0
                 success = 0
                 for _, row in df.iterrows():
                     semester = Semester.objects.filter(sem_id=row['Sem ID']).first()
                     if not semester:
                         instance = Semester(sem_id=row['Sem ID'], semester_name=row['Sem Name'])
                         instance.save()
                         success+=1
                     else:
                         contexts.append(f'Duplicate semester with sem id {row["Sem ID"]} was skipped.')
                         error+=1
                         
            elif upload_type == 'students':
                 error = 0
                 success = 0
                 for _, row in df.iterrows():
                     student = Student.objects.filter(roll_number=row['Roll Number']).first()
                     if not student:
                         instance = Student(roll_number=row['Roll Number'], name=row['Name'])
                         instance.save()
                         success+=1
                     else:
                         contexts.append(f'Duplicate student entry with roll number {row["Roll Number"]} was skipped.')
                         error+=1
                #  contexts.append(f'Databse is updated for {success} rows and {error} rows were skipped')

            elif upload_type == 'courses':
                 error=0
                 success=0
                 for _, row in df.iterrows():
                     course = Course.objects.filter(course_code=row['Course Code']).first()
                     if not course:
                         instance = Course(course_code=row['Course Code'], course_name=row['Course Name'], credits=row['Credits'])
                         instance.save()
                         success+=1
                     else:
                         contexts.append(f'Duplicate course entry with course code {row["Course Code"]} was skipped.')
                         error+=1
                #  contexts.append(f'Databse is updated for {success} rows and {error} rows were skipped')

            elif upload_type == 'enrollment':
                print("contunue")
                error=0
                success=0
                for index, row in df.iterrows():
                    logger.info(f"Processing row {index}")
                    student = Student.objects.filter(roll_number=row['Roll Number']).first()
                    semester = Semester.objects.filter(sem_id=row['Semester']).first()
                    course = Course.objects.filter(course_code=row['Course Code']).first()
                    enrollment = Enrollment.objects.filter(roll_number=student, sem_id=semester, course_code=course)
                    if not student:
                        contexts.append(f'No student found with roll number {row["Roll Number"]}.')
                        error+=1
                        continue
                
                    if not semester:
                        contexts.append(f'No semester found with semester id {row["Semester"]}.')
                        error+=1
                        continue
                    
                    if not course:
                        contexts.append(f'No course found with course code {row["Course Code"]}.')
                        error+=1   
                        continue                    
                
                    if enrollment:
                        contexts.append(f'entry with {row["Roll Number"]}, {row["Semester"]}, {row["Course Code"]}, {row["Grade"]} was skipped.')
                        error+=1
                        continue
                    else:
                        try:
                            instance = Enrollment(roll_number=student, sem_id=semester, course_code=course, grade=row['Grade'])
                            instance.save()
                            success += 1
                            # logger.info(f"Enrollment added for {row['Roll Number']}, {row['Semester']}, {row['Course Code']}")
                        except Exception as e:
                            logger.error(f"Error saving enrollment for row {index}: {e}")
                            error += 1

            else:
                 return JsonResponse({'message': 'Invalid upload type.'})  
        
        except Exception as e:
            logger.error(f"Error processing Excel file: {e}")
        
        finally:
             default_storage.delete(temp_path)
             contexts = remove_duplicates(contexts)
             return JsonResponse({
                 'message': 'An excel file is received.',
                 'context': contexts,
                 'success' : success,
                 'error' : error
             })
     else:
         return JsonResponse({'error': 'Invalid request'}, status=400)


def export_enrollment_data(request):
    # Get query parameters for student roll number and CGPA range
    student_roll_number = request.GET.get('student_roll_number', None)
    min_cgpa = request.GET.get('min_cgpa', 0.0)
    max_cgpa = request.GET.get('max_cgpa', 4.0)

    # Query the Enrollment model to get all enrollment records
    enrollments = Enrollment.objects.all()
    students = Student.objects.all()

    # Filter by student roll number if provided
    if student_roll_number:
        enrollments = enrollments.filter(roll_number__roll_number__icontains=student_roll_number)

    # Filter by CGPA range if provided
    if min_cgpa and max_cgpa:
        students = students.filter(cgpa__gte=min_cgpa, cgpa__lte=max_cgpa)
        enrollments = enrollments.filter(roll_number__in=students.values_list('roll_number', flat=True))

    # Convert the queryset to a pandas DataFrame
    df = pd.DataFrame.from_records(enrollments.values())

    # Create a BytesIO object to hold the Excel data
    excel_data = BytesIO()

    # Write the DataFrame to the BytesIO object using pandas.ExcelWriter
    with pd.ExcelWriter(excel_data, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Enrollment Data')

    # Set the content type and headers for the response
    excel_data.seek(0) # Move the cursor to the beginning of the BytesIO object
    response = HttpResponse(excel_data.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=enrollment_data.xlsx'

    return response
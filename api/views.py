from django.shortcuts import render, redirect ,HttpResponseRedirect
from django.http import JsonResponse
from django.db import connection
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.core.serializers.json import DjangoJSONEncoder
from django.core.serializers import serialize
import json
import pandas as pd
from grading.models import Student, Enrollment ,SGPA
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from grading.views import GRADE_WEIGHTS
dictToExport = {}
def index(request):
    return render(request,'authentication/index.html')

# Login Authentication
def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(username = username, password = password)
        
        if user is not None:
            login(request,user)
            username = user.username
            return redirect('admin_home')
        else:
            messages.error(request, "Incorrect Credentials!")
            return redirect('index')
    return render(request, "authentication/index.html")

def admin_home(request):
    return render(request, 'authentication/admin.html')

@login_required
def signout(request):
    logout(request)
    return redirect('index')
    
@csrf_exempt  
@require_GET
def all_students(request, input):
    global dictToExport
    students = Student.objects.filter(roll_number__contains=input)
    student_list = [model_to_dict(student) for student in students]
    request.session['dictToExport'] = student_list
    return JsonResponse({'students': student_list}, safe=False)

@csrf_exempt
@require_GET
def specific_student(request, input):
    global dictToExport
    batch = request.GET.get('batch', None)
    if batch:
        students = Student.objects.filter(roll_number__startswith=batch)
        students = students.filter(
            Q(name__icontains=input) | Q(roll_number__contains=input)
        )
    else:
        students = Student.objects.filter(
            Q(name__icontains=input) | Q(roll_number__contains=input)
        )
    
    student_list = [model_to_dict(student) for student in students]
    request.session['dictToExport'] = student_list
    return JsonResponse({'students': student_list}, safe=False)

@csrf_exempt
@require_GET
def get_student_by_cgpa(request, input):
    global dictToExport
    batch = request.GET.get('batch', None)
    input = float(input)

    students = Student.objects.filter(roll_number__startswith=batch ,cgpa__lt = input)
    student_list = [model_to_dict(student) for student in students]
    request.session['dictToExport'] = student_list
    return JsonResponse({'students': student_list}, safe=False)

@csrf_exempt
@require_GET
def get_student_by_cgpa_and_major(request, input):
    global dictToExport
    batch = request.GET.get('batch', None)
    major = request.GET.get('major' , None)
    input = float(input)

    print(batch)
    print(major)
    print(input)
    if major:
        students = Student.objects.filter(
            roll_number__startswith=batch,
            roll_number__contains=major,
            cgpa__lt=input
        )
    else:
        # If no major is provided, filter by batch and CGPA only
        students = Student.objects.filter(
            roll_number__startswith=batch,
            cgpa__lt=input
        )
    student_list = [model_to_dict(student) for student in students]
    request.session['dictToExport'] = student_list
    return JsonResponse({'students': student_list}, safe=False)
    
@csrf_exempt
@require_GET
def getStudentGrades(request, input):
    print(input)
    try:
        # input = input.lower()
        student = Student.objects.get(pk=input)
        
        student_dict = {'grades': []}
        enrollments = Enrollment.objects.filter(roll_number=student)
        cgpa_value = student.cgpa
        name = student.name
        
        total_credit_points = 0
        total_weighted_points = 0
        retaken_courses = {}
        
        for enrollment in enrollments:

            sgpa = SGPA.objects.filter(roll_number=student, sem_id=enrollment.sem_id).first()
            sgpa_value = sgpa.value if sgpa else None
            
            grade_value = enrollment.grade.upper()
            credit_points = enrollment.course_code.credits
            weighted_points = GRADE_WEIGHTS.get(grade_value, 0.0)
            
            grade_info = {
                'course_code': enrollment.course_code.course_code,
                'course_name': enrollment.course_code.course_name,
                'sem_id': enrollment.sem_id.sem_id,
                'grade': enrollment.grade ,
                'sgpa' : sgpa_value,           
            }
            student_dict['grades'].append(grade_info)
            
            if grade_value == 'RC':
                continue # Skip this iteration if the grade is "RC"

            course_code = enrollment.course_code.course_code
            if course_code in retaken_courses:
                try:
                # If the course has been retaken, check if the new grade is higher than the highest grade stored
                
                    if GRADE_WEIGHTS[grade_value] > GRADE_WEIGHTS[retaken_courses[course_code][0]]:
                        # Deduct the credit points and weighted points of the previous attempt
                        total_credit_points -= retaken_courses[course_code][1] * credit_points
                        total_weighted_points -= retaken_courses[course_code][1] * (GRADE_WEIGHTS[retaken_courses[course_code][0]] * credit_points)
                        # Update the retaken courses dictionary with the new grade and increment the attempt count
                        retaken_courses[course_code] = (grade_value, retaken_courses[course_code][1] + 1)
                    else:
                        # If the new grade is not higher, do not update the dictionary but still deduct the previous attempt's points
                        total_credit_points -= credit_points
                        total_weighted_points -= weighted_points * credit_points
                except Exception as e:
                    print(f"an error occured : {e}")
                
            else:
                # If the course has not been retaken, add it to the dictionary
                retaken_courses[course_code] = (grade_value, 1)

            total_credit_points += credit_points  

            total_weighted_points += (weighted_points * credit_points)

        return JsonResponse({'grades': student_dict['grades'], 'cgpa': cgpa_value,'name': name , 'roll_num':input , 'total_credit_points' : total_credit_points})
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Student does not exist.'}, status=404)
    
@csrf_exempt
@require_GET
def recommendation(request , input):
    new_credit_point = int(input)
    roll_num = request.GET.get('roll_num' , None)
    print(roll_num)
    total_credit_points = 0
    total_weighted_points = 0
    
    student = Student.objects.filter(roll_number=roll_num).first()
    enrollments = Enrollment.objects.filter(roll_number=roll_num).order_by('sem_id')

    retaken_courses = {}
    
    current_cgpa = student.cgpa
    
    for enrollment in enrollments:
        grade_value = enrollment.grade.upper()
        credit_points = enrollment.course_code.credits
        weighted_points = GRADE_WEIGHTS.get(grade_value, 0.0)

        if grade_value == 'RC':
            continue # Skip this iteration if the grade is "RC"

        course_code = enrollment.course_code.course_code
        if course_code in retaken_courses:
            try:
            # If the course has been retaken, check if the new grade is higher than the highest grade stored
            
                if GRADE_WEIGHTS[grade_value] > GRADE_WEIGHTS[retaken_courses[course_code][0]]:
                    # Deduct the credit points and weighted points of the previous attempt
                    total_credit_points -= retaken_courses[course_code][1] * credit_points
                    total_weighted_points -= retaken_courses[course_code][1] * (GRADE_WEIGHTS[retaken_courses[course_code][0]] * credit_points)
                    # Update the retaken courses dictionary with the new grade and increment the attempt count
                    retaken_courses[course_code] = (grade_value, retaken_courses[course_code][1] + 1)
                else:
                    # If the new grade is not higher, do not update the dictionary but still deduct the previous attempt's points
                    total_credit_points -= credit_points
                    total_weighted_points -= weighted_points * credit_points
            except Exception as e:
                print(f"an error occured : {e}")
            
        else:
            # If the course has not been retaken, add it to the dictionary
            retaken_courses[course_code] = (grade_value, 1)

        total_credit_points += credit_points
        
        total_weighted_points += (weighted_points * credit_points)

    
    print(f'current cgpa = {current_cgpa}' )
    print(f'credit point offered in next sem = {new_credit_point}')
    print(f'total credit point = {total_credit_points}')
    
    total_grade_points_needed =  2.0 * (total_credit_points + new_credit_point)
    current_total_grade_point = current_cgpa * total_credit_points
    grade_points_needed = total_grade_points_needed - current_total_grade_point
    average_grade_point = grade_points_needed / new_credit_point
    
    print(f'current total grade point = {current_total_grade_point}')
    print(f'average grade point needed = {average_grade_point}')
    return JsonResponse({ 'grade_weights' : GRADE_WEIGHTS ,'average_grade_point' : average_grade_point , 
                          'credit_point_offered_next_sem' : new_credit_point,
                         'current_total_credit_points' : total_credit_points })
                             
    '''
    for enrollment in enrollments:
        credit_points = enrollment.course_code.credits
        grade_value = enrollment.grade.upper()

        if grade_value == 'F':
            if enrollment.course_code.course_code in failed_courses:
                print(enrollment.course_code.course_code)
                failed_courses[enrollment.course_code.course_code] +=  1
                print(f' failed courses :{failed_courses}')
            else:
                failed_courses[enrollment.course_code.course_code] =  1
                print(f' failed courses :{failed_courses}')
        else:
            if enrollment.course_code.course_code in failed_courses:
                accumulated_credit_points -= (failed_courses[enrollment.course_code.course_code] * credit_points)
                # for _ in range(failed_courses[enrollment.course_code.course_code]):
                # accumulated_credit_points -= credit_points
                
                del failed_courses[enrollment.course_code.course_code]

        accumulated_credit_points += credit_points
        '''


@csrf_exempt
@require_POST
def export_students_to_excel(request):
    # Parse the JSON data from the request body
    data = json.loads(request.body)

    # Check if the 'isExportRequest' key is present in the data
    is_export_request = data.get('isExportRequest', False)


    # Retrieve the data dictionary from the session
    data_dict = request.session.get('dictToExport', {})
    if is_export_request:
        try:
            data_dict_sorted = sorted(data_dict, key=lambda x: x['roll_number'].split('-')[2])
            for student in data_dict_sorted:
                student['cgpa'] = round(student['cgpa'],3)
            # Convert the dictionary to a pandas DataFrame
            df = pd.DataFrame(data_dict_sorted)
            # Create a response object with the appropriate content type
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=student_list.xlsx'
            # Export the DataFrame to an Excel file and write it to the response
            df.to_excel(response, index=False)
            # Clear the session data after exporting
            request.session['dictToExport'] = None
            return response
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
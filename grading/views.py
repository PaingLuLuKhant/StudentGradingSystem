'''
from grading.models import Enrollment

GRADE_WEIGHTS = {
    'A': 4.0,
    'A-': 3.7,
    'B+': 3.4,
    'B': 3.0,
    'B-': 2.7,
    'C+': 2.4,
    'C': 2.0,
    'D': 1.0,
    'F': 0.0,
    'RC' : 0 
}

def calculate_sgpa(roll_number, sem_id):
    enrollments = Enrollment.objects.filter(roll_number=roll_number, sem_id=sem_id)
    total_credit_points = 0
    total_weighted_points = 0

    for enrollment in enrollments:
        grade_value = enrollment.grade.upper()
        
        if grade_value == 'RC':
            continue  # Skip this iteration if the grade is "RC"
   
        credit_points = enrollment.course_code.credits
        weighted_points = GRADE_WEIGHTS.get(grade_value,0.0)
        
        total_credit_points += credit_points
        total_weighted_points += (weighted_points * credit_points)

    if total_credit_points ==   0:
        return   0.0  # Avoid division by zero

    sgpa = total_weighted_points / total_credit_points
    return sgpa

def calculate_cgpa(roll_number):
    enrollments = Enrollment.objects.filter(roll_number=roll_number).order_by('sem_id')
    total_credit_points =  0
    total_weighted_points =  0
    failed_courses = {}

    for enrollment in enrollments:
        grade_value = enrollment.grade.upper()
        credit_points = enrollment.course_code.credits
        weighted_points = GRADE_WEIGHTS.get(grade_value,  0.0)
        
        if grade_value == 'RC':
            print(f'Rc course {enrollment.course_code}')
            continue
        
        else:
            if grade_value == 'F':
                if enrollment.course_code.course_code in failed_courses:
                    print(enrollment.course_code.course_code)
                    failed_courses[enrollment.course_code.course_code] +=  1

                else:
                    failed_courses[enrollment.course_code.course_code] =  1

            else:
                if enrollment.course_code.course_code in failed_courses:
                    total_credit_points -= (failed_courses[enrollment.course_code.course_code] * credit_points)

                    del failed_courses[enrollment.course_code.course_code]

            total_credit_points += credit_points
            total_weighted_points += (weighted_points * credit_points)

    if total_credit_points ==  0:
        return  0.0  # Avoid division by zero

    print(total_weighted_points)
    print(total_credit_points)
    cgpa = total_weighted_points / total_credit_points
    
    return cgpa
'''
from grading.models import Enrollment

GRADE_WEIGHTS = {
    'A': 4.0,
    'A-': 3.7,
    'B+': 3.4,
    'B': 3.0,
    'B-': 2.7,
    'C+': 2.4,
    'C': 2.0,
    'D': 1.0,
    'F': 0.0,
    'RC' : 0 
}

def calculate_sgpa(roll_number, sem_id):
    enrollments = Enrollment.objects.filter(roll_number=roll_number, sem_id=sem_id)
    total_credit_points = 0
    total_weighted_points = 0

    for enrollment in enrollments:
        grade_value = enrollment.grade.upper()
        
        if grade_value == 'RC':
            continue  # Skip this iteration if the grade is "RC"
   
        credit_points = enrollment.course_code.credits
        weighted_points = GRADE_WEIGHTS.get(grade_value,0.0)
        
        total_credit_points += credit_points
        total_weighted_points += (weighted_points * credit_points)

    if total_credit_points ==   0:
        return   0.0  # Avoid division by zero

    sgpa = total_weighted_points / total_credit_points
    return sgpa

def calculate_cgpa(roll_number):
    enrollments = Enrollment.objects.filter(roll_number=roll_number).order_by('sem_id')
    total_credit_points = 0
    total_weighted_points = 0
    retaken_courses = {} # Track retaken courses and their highest grade

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
        print(total_credit_points)
        
        total_weighted_points += (weighted_points * credit_points)

    if total_credit_points == 0:
        return 0.0 # Avoid division by zero

    cgpa = total_weighted_points / total_credit_points
    return cgpa
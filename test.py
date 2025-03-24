import pandas as pd
import json
import numpy as np

def convert_to_native_types(obj):
    if isinstance(obj, (np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, dict):
        return {key: convert_to_native_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_native_types(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_to_native_types(item) for item in obj)
    else:
        return obj

file_path = 'dataset.xlsx'
course_list = pd.read_excel(file_path, sheet_name='Course list')
rooms_data = pd.read_excel(file_path, sheet_name='Rooms data')
lecturer_details = pd.read_excel(file_path, sheet_name='Lecturer Details')
student_list = pd.read_excel(file_path, sheet_name='Student requests')

course_list.columns = course_list.columns.str.lower().str.replace(' ', '_')
rooms_data.columns = rooms_data.columns.str.lower().str.replace(' ', '_')
lecturer_details.columns = lecturer_details.columns.str.lower().str.replace(' ', '_')
student_list.columns = student_list.columns.str.lower().str.replace(' ', '_')

course_list = course_list.fillna({'available_blocks': '', 'unavailable_blocks': ''})
rooms_data = rooms_data.fillna({'room_number': 0})
lecturer_details = lecturer_details.fillna({'section_number': 0})
student_list = student_list.fillna({'type': 'Requested'})

course_list = course_list.drop_duplicates()
rooms_data = rooms_data.drop_duplicates()
lecturer_details = lecturer_details.drop_duplicates()
student_list = student_list.drop_duplicates()

course_list['length'] = course_list['length'].astype(int)
rooms_data['room_number'] = rooms_data['room_number'].astype(int)
lecturer_details['length'] = lecturer_details['length'].astype(int)
student_list['length'] = student_list['length'].astype(int)

lecturer_id_to_code = lecturer_details.set_index('lecturer_id')['lecture_code'].to_dict()
student_list['course_code'] = student_list['course_id'].map(lecturer_id_to_code)

nan_course_codes = student_list[student_list['course_code'].isna()]
if not nan_course_codes.empty:
    print("\nWarning: The following students have invalid or missing course codes:")
    print(nan_course_codes[['student_id', 'course_id', 'course_code']])
    student_list = student_list.dropna(subset=['course_code'])

teacher_block_counts = lecturer_details.groupby(['lecturer_id', 'start_term', 'section_number']).size()
duplicate_teacher_assignments = teacher_block_counts[teacher_block_counts > 1]
if not duplicate_teacher_assignments.empty:
    print("\nDuplicate teacher assignments detected:")
    print(duplicate_teacher_assignments)
else:
    print("\nNo duplicate teacher assignments found.")

student_block_counts = student_list.groupby(['student_id', 'request_start_term', 'course_id']).size()
duplicate_student_assignments = student_block_counts[student_block_counts > 1]
if not duplicate_student_assignments.empty:
    print("\nDuplicate student assignments detected:")
    print(duplicate_student_assignments)
else:
    print("\nNo duplicate student assignments found.")

student_counts_per_course = student_list['course_code'].value_counts()

if 'maximum_section_size' not in course_list.columns:
    raise ValueError("Column 'maximum_section_size' not found in course_list.")

course_list = course_list.set_index('course_code')
student_counts_per_course = student_counts_per_course[student_counts_per_course.index.isin(course_list.index)]
course_list_aligned = course_list.loc[student_counts_per_course.index]

overcrowded_courses = student_counts_per_course[student_counts_per_course > course_list_aligned['maximum_section_size']]

if not overcrowded_courses.empty:
    print("\nOvercrowded courses detected:")
    print(overcrowded_courses)
else:
    print("\nNo overcrowded courses found.")

course_list_json = course_list.reset_index().to_json(orient='records')
rooms_data_json = rooms_data.to_json(orient='records')
lecturer_details_json = lecturer_details.to_json(orient='records')
student_list_json = student_list.to_json(orient='records')

with open('course_list.json', 'w') as f:
    f.write(course_list_json)

with open('rooms_data.json', 'w') as f:
    f.write(rooms_data_json)

with open('lecturer_details.json', 'w') as f:
    f.write(lecturer_details_json)

with open('student_list.json', 'w') as f:
    f.write(student_list_json)

most_requested_courses = student_list['course_code'].value_counts().head(10)
print("\nTop 10 most requested courses:")
print(most_requested_courses)

courses_without_rooms = course_list[course_list['available_blocks'] == '']
if not courses_without_rooms.empty:
    print("\nCourses with no available rooms:")
    print(courses_without_rooms[['title']])
else:
    print("\nAll courses have available rooms.")

courses_without_lecturers = course_list[~course_list.index.isin(lecturer_details['lecture_code'])]
if not courses_without_lecturers.empty:
    print("\nCourses with no lecturers:")
    print(courses_without_lecturers[['title']])
else:
    print("\nAll courses have lecturers.")

priority_counts = student_list['type'].value_counts()
print("\nPriority distribution of student requests:")
print(priority_counts)

def assign_students_to_sections(course_list, student_list, lecturer_details, block_schedule):
    schedule = {}
    priority_map = {"Required": 1, "Requested": 2, "Recommended": 3}
    student_list['priority_value'] = student_list['type'].map(priority_map)
    student_list = student_list.sort_values(by='priority_value')
    course_to_block = {}
    for block, courses in block_schedule.items():
        for course in courses:
            course_code = course['course_code']
            if course_code not in course_to_block:
                course_to_block[course_code] = block
    student_block_assignments = {}
    for _, student_request in student_list.iterrows():
        student_id = student_request['student_id']
        course_code = student_request['course_code']
        if course_code not in course_to_block:
            print(f"\nWarning: Course {course_code} not found in block schedule. Skipping.")
            continue
        assigned_block = course_to_block[course_code]
        if student_id in student_block_assignments and assigned_block in student_block_assignments[student_id]:
            print(f"\nWarning: Student {student_id} already assigned to block {assigned_block}. Skipping.")
            continue
        section_key = f"{course_code}_Section1"
        if section_key not in schedule:
            lecturer_assigned = lecturer_details[lecturer_details['lecture_code'] == course_code]
            if len(lecturer_assigned) == 0:
                print(f"\nWarning: No lecturer assigned to course {course_code}. Skipping.")
                continue
            lecturer_id = lecturer_assigned['lecturer_id'].values[0]
            schedule[section_key] = {
                "block": assigned_block,
                "students": [],
                "lecturer": lecturer_id
            }
        schedule[section_key]["students"].append(student_id)
        if student_id not in student_block_assignments:
            student_block_assignments[student_id] = []
        student_block_assignments[student_id].append(assigned_block)
    balanced_schedule = balance_sections(schedule, course_list)
    return balanced_schedule

def balance_sections(schedule, course_list):
    course_sections = {}
    for section_key, section_data in schedule.items():
        course_code = section_key.split('_')[0]
        if course_code not in course_sections:
            course_sections[course_code] = []
        course_sections[course_code].append(section_key)
    for course_code, section_keys in course_sections.items():
        if len(section_keys) <= 1:
            continue
        try:
            max_size = course_list.loc[course_code, 'maximum_section_size']
        except:
            continue
        all_students = []
        for section_key in section_keys:
            all_students.extend(schedule[section_key]["students"])
        students_per_section = min(len(all_students) // len(section_keys), max_size)
        student_index = 0
        for section_key in section_keys:
            end_index = min(student_index + students_per_section, len(all_students))
            schedule[section_key]["students"] = all_students[student_index:end_index]
            student_index = end_index
            if student_index >= len(all_students):
                break
    return schedule

def assign_courses_to_blocks(course_list, lecturer_details):
    block_schedule = {block: [] for block in ["1A", "1B", "2A", "2B", "3", "4A", "4B"]}
    lecturer_block_assignments = {}
    course_data = []
    for course_code, course_info in course_list.iterrows():
        lecturer_assigned = lecturer_details[lecturer_details['lecture_code'] == course_code]
        if len(lecturer_assigned) == 0:
            print(f"\nWarning: No lecturer assigned to course {course_code}. Skipping.")
            continue
        available_blocks = course_info['available_blocks'].split(',') if course_info['available_blocks'] else []
        unavailable_blocks = course_info['unavailable_blocks'].split(',') if course_info['unavailable_blocks'] else []
        valid_blocks = [block.strip() for block in available_blocks if block.strip() not in [b.strip() for b in unavailable_blocks]]
        if not valid_blocks:
            print(f"\nWarning: No valid blocks for course {course_code}. Skipping.")
            continue
        lecturer_id = lecturer_assigned['lecturer_id'].values[0]
        course_data.append({
            "course_code": course_code,
            "lecturer_id": lecturer_id,
            "valid_blocks": valid_blocks,
            "sections": course_info['number_of_sections']
        })
    course_data.sort(key=lambda x: len(x['valid_blocks']))
    for course in course_data:
        assigned = False
        for block in course['valid_blocks']:
            clean_block = block.strip()
            if clean_block not in block_schedule:
                print(f"\nWarning: Invalid block name '{block}' for course {course['course_code']}. Skipping.")
                continue
            if course['lecturer_id'] in lecturer_block_assignments.get(clean_block, []):
                continue
            block_schedule[clean_block].append({
                "course_code": course['course_code'],
                "lecturer": course['lecturer_id']
            })
            if clean_block not in lecturer_block_assignments:
                lecturer_block_assignments[clean_block] = []
            lecturer_block_assignments[clean_block].append(course['lecturer_id'])
            assigned = True
            break
        if not assigned:
            print(f"\nWarning: Could not assign course {course['course_code']} to any block due to lecturer conflicts.")
    return block_schedule

block_schedule = assign_courses_to_blocks(course_list, lecturer_details)
schedule = assign_students_to_sections(course_list, student_list, lecturer_details, block_schedule)

with open('block_schedule.json', 'w') as f:
    json.dump(convert_to_native_types(block_schedule), f, indent=4)

with open('schedule.json', 'w') as f:
    json.dump(convert_to_native_types(schedule), f, indent=4)

print("\nBlock schedule has been saved to 'block_schedule.json'.")
print("\nStudent assignments have been saved to 'schedule.json'.")

def classify_courses_by_length(course_list):
    course_list['duration'] = course_list['length'].apply(lambda x: "Full Year" if x == 2 else "Half Year")
    return course_list

course_list = classify_courses_by_length(course_list)

course_list_json = course_list.reset_index().to_json(orient='records')
with open('course_list_with_duration.json', 'w') as f:
    f.write(course_list_json)

print("\nCourse list with duration has been saved to 'course_list_with_duration.json'.")

with open('insights_report.txt', 'w') as f:
    f.write("Data Cleaning and Validation Report\n")
    f.write("==================================\n")
    f.write("1. Duplicate Teacher Assignments:\n")
    f.write(str(duplicate_teacher_assignments) + "\n\n")
    f.write("2. Duplicate Student Assignments:\n")
    f.write(str(duplicate_student_assignments) + "\n\n")
    f.write("3. Overcrowded Courses:\n")
    f.write(str(overcrowded_courses) + "\n\n")
    f.write("4. Most Requested Courses:\n")
    f.write(str(most_requested_courses) + "\n\n")
    f.write("5. Courses with No Available Rooms:\n")
    f.write(str(courses_without_rooms[['title']]) + "\n\n")
    f.write("6. Courses with No Lecturers:\n")
    f.write(str(courses_without_lecturers[['title']]) + "\n\n")
    f.write("7. Priority Distribution of Student Requests:\n")
    f.write(str(priority_counts) + "\n\n")
    f.write("8. Student Assignments to Sections:\n")
    f.write(json.dumps(convert_to_native_types(schedule), indent=4) + "\n\n")
    f.write("9. Block Schedule:\n")
    f.write(json.dumps(convert_to_native_types(block_schedule), indent=4) + "\n\n")
    f.write("10. Course Duration Classification:\n")
    f.write(course_list[['title', 'duration']].to_string() + "\n\n")

print("\nInsights and validation results have been saved to 'insights_report.txt'.")
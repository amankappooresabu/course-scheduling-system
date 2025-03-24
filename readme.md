# Course Scheduling and Student Assignment System

This project is a Python-based system designed to manage course scheduling, student assignments, and room allocations for educational institutions. It processes data from Excel files, performs data cleaning and validation, and generates schedules and insights in JSON format.

## Features

- **Data Cleaning**: Standardizes column names, handles missing values, and ensures consistent data types.
- **Data Validation**: Checks for duplicate teacher and student assignments, and ensures sections are not overcrowded.
- **Course Scheduling**: Assigns courses to specific blocks while considering lecturer availability and room constraints.
- **Student Assignment**: Assigns students to course sections based on priority and availability.
- **Insights Generation**: Provides insights such as most requested courses, courses without rooms, and priority distribution of student requests.
- **JSON Output**: Saves cleaned data, schedules, and insights in JSON files for further use.

## Requirements

- Python 3.x
- pandas
- numpy
- openpyxl

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/course-scheduling-system.git
   cd course-scheduling-system
   ```

2. Install the required packages:
   ```bash
   pip install pandas numpy openpyxl
   ```

## Usage

1. **Prepare Your Data**: Ensure your Excel file (`dataset.xlsx`) contains the following sheets:
   - **Course list**: Contains course details.
   - **Rooms data**: Contains room details.
   - **Lecturer Details**: Contains lecturer details.
   - **Student requests**: Contains student course requests.

2. **Run the Script**:
   ```bash
   python main.py
   ```

3. **Output Files**:
   - `course_list.json`: Cleaned course list data.
   - `rooms_data.json`: Cleaned room data.
   - `lecturer_details.json`: Cleaned lecturer details.
   - `student_list.json`: Cleaned student requests.
   - `block_schedule.json`: Generated block schedule.
   - `schedule.json`: Generated student assignments.
   - `course_list_with_duration.json`: Course list with duration classification.
   - `insights_report.txt`: Insights and validation results.

## Example

### Input (`dataset.xlsx`)

#### Course list:
| course_code | title            | length | available_blocks | unavailable_blocks | maximum_section_size | number_of_sections |
|------------|-----------------|--------|------------------|--------------------|----------------------|--------------------|
| MATH101    | Mathematics 101 | 1      | 1A,2A           | 1B                 | 30                   | 2                  |

#### Rooms data:
| room_number | capacity |
|------------|----------|
| 101        | 50       |

#### Lecturer Details:
| lecturer_id | lecture_code | start_term | section_number | length |
|------------|--------------|------------|----------------|--------|
| L001       | MATH101      | 1A         | 1              | 1      |

#### Student requests:
| student_id | course_id | request_start_term | type     | length |
|-----------|-----------|--------------------|---------|--------|
| S001      | MATH101   | 1A                 | Required | 1      |


## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contact

For any questions or feedback, please reach out to [your email address].

**Note**: Replace placeholders like `yourusername`, `your email address`, and adjust the example data as needed.


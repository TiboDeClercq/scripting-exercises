import argparse
import datetime
import sys
import csv
import re


def _row_date(row):
    d, m, y = row['Datum'].split('-')
    return datetime.date(2000+int(y), int(m), int(d))


def _format_row(row, format_string):
    format_string = format_string.replace('%d', row['Datum'])
    format_string = format_string.replace('%c', row['OLA Naam'])
    format_string = format_string.replace('%l', row['Lokaal'])
    format_string = format_string.replace('%s', row['Startuur'])
    format_string = format_string.replace('%i', row['Student ID'])

    return format_string


def _student_command(args):
    with open(args.filename) as file:
        reader = csv.DictReader(file)
        relevant_rows = []

        for row in reader:
            if row['Student ID'] == args.id:
                relevant_rows.append(row)

        relevant_rows.sort(key=_row_date)

        for row in relevant_rows:
            print(_format_row(row, args.format))


def _lecturer_command(args):
    with open(args.filename) as file:
        reader = csv.DictReader(file)
        relevant_rows = []

        for row in reader:
            if args.id in row['Lector']:
                relevant_rows.append(row)

        relevant_rows.sort(key=_row_date)

        for row in relevant_rows:
            print(_format_row(row, args.format))


def _course_command(args):
    with open(args.filename) as file:
        reader = csv.DictReader(file)
        relevant_rows = []

        for row in reader:
            if re.search(args.pattern, row['OLA Naam']):
                relevant_rows.append(row)

        relevant_rows.sort(key=_row_date)

        for row in relevant_rows:
            print(_format_row(row, args.format))


def _exam_counts_command(args):
    exam_counts = {}

    with open(args.filename) as file:
        reader = csv.DictReader(file)

        for row in reader:
            student_id = row['Student ID']

            if student_id not in exam_counts:
                exam_counts[student_id] = 1
            else:
                exam_counts[student_id] += 1

    exam_counts = list(exam_counts.items())
    exam_counts.sort(key=lambda x: x[1])

    for student, exam_count in exam_counts:
        print(f'{student} {exam_count}')


def _multiple_command(args):
    exam_counts = {}

    with open(args.filename) as file:
        reader = csv.DictReader(file)

        for row in reader:
            student_id = row['Student ID']
            date = _row_date(row)
            key = (student_id, date)

            if key not in exam_counts:
                exam_counts[key] = 1
            else:
                exam_counts[key] += 1

    exam_counts = [ (id, n) for id, n in exam_counts.items() if n > 1 ]
    exam_counts.sort(key=lambda x: x[1])

    for (student, date), exam_count in exam_counts:
        print(f'{student} {date} {exam_count}')


def process_command_line_arguments():
    # Top level parser
    parser = argparse.ArgumentParser(prog='exam-schedule')
    parser.add_argument('filename', help='.csv file to consult')
    parser.set_defaults(func=lambda args: parser.print_help())
    subparsers = parser.add_subparsers(help='sub-command help')

    # Command 'student'
    student_parser = subparsers.add_parser('student', help='shows exams of student')
    student_parser.add_argument('id', help='student id')
    student_parser.add_argument('--format', help='format string', default='%d %c')
    student_parser.set_defaults(func=_student_command)

    # Command 'lecturer'
    lecturer_parser = subparsers.add_parser('lecturer', help='shows exams of lecturer')
    lecturer_parser.add_argument('id', help='lecturer id')
    lecturer_parser.add_argument('--format', help='format string', default='%d %c')
    lecturer_parser.set_defaults(func=_lecturer_command)

    # Command 'course'
    course_parser = subparsers.add_parser('course', help='shows exams of course')
    course_parser.add_argument('pattern', help='pattern for course name')
    course_parser.add_argument('--format', help='format string', default='%d %i %l')
    course_parser.set_defaults(func=_course_command)

    # Command 'exam-counts'
    exam_counts_parser = subparsers.add_parser('exam-counts', help='number of exams per student')
    exam_counts_parser.set_defaults(func=_exam_counts_command)

    # Command 'multiple'
    multiple_parser = subparsers.add_parser('multiple', help='shows students with multiple exams')
    multiple_parser.set_defaults(func=_multiple_command)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    process_command_line_arguments()
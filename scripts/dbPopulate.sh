#!/bin/bash

sudo su - postgres -c 'psql -c "
delete from attendance_course_student_list where id>-1;
delete from attendance_user where id>-1;
delete from attendance_coursecode where id>-1;
delete from attendance_attendancerecord where id>-1;
"'

python3.5 manage.py shell <<SCRIPT
from attendance.models import *
u1 = User()
u1.isInstructor = True
u1.first_name = 'John'
u1.last_name = 'Doe'
u1.cuid = 500500
u1.username = 'jdoe'
u1.save()

u2 = User()
u2.isInstructor = True
u2.first_name = 'Jane'
u2.last_name = 'Doe'
u2.cuid = 808080
u2.username = 'jdoe2'
u2.save()


s1 = User()
s1.first_name = 'Student1'
s1.last_name = 'One'
s1.cuid = 11111
s1.username = 'studone1'
s1.save()

s2 = User()
s2.first_name = 'Student2'
s2.last_name = 'Two'
s2.cuid = 222222
s2.username = 'studtwo2'
s2.save()

s3 = User()
s3.first_name = 'Student3'
s3.last_name = 'Three'
s3.cuid = 333333
s3.username = 'studthree3'
s3.save()

c = Course(name = "tc101", instructorusername='jdoe')
c.save()
c.student_list.add(s2)
c.student_list.add(s3)
c.save()
SCRIPT

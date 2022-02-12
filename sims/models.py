from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager, AbstractBaseUser


class Class(models.Model):
    """班级"""
    class_id = models.IntegerField(primary_key=True, verbose_name="班级ID")
    class_name = models.CharField(max_length=30)

    class Meta:
        verbose_name = '班级表'

    def __str__(self):
        return str(self.class_id) + " " + self.class_name


class User(AbstractBaseUser):
    ROLE_CHOICES = [
        ('0', 'Teacher'),
        ('1', 'Student')
    ]
    user_id = models.IntegerField(primary_key=True, verbose_name="用户ID")
    name = models.CharField(max_length=30, verbose_name='姓名', default='')
    age = models.IntegerField(verbose_name="年龄", default=0)
    username = models.CharField(max_length=10, verbose_name='用户名', unique=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default=0)
    password = models.CharField(max_length=256, verbose_name='密码')
    last_login = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name='最后登录时间')
    objects = UserManager()
    USERNAME_FIELD = 'username'

    class Meta:
        verbose_name = '用户'

    def __str__(self):
        return self.name


class Student(models.Model):
    """学生"""
    student = models.OneToOneField(User, related_name='user_student', verbose_name="学生ID", on_delete=models.CASCADE)
    class_name = models.ForeignKey(Class, related_name='course_student', on_delete=models.CASCADE)

    class Meta:
        verbose_name = '学生'

    def __str__(self):
        return self.student_id


class Teacher(models.Model):
    """教师"""
    teacher = models.OneToOneField(User, verbose_name="教师ID", on_delete=models.CASCADE)

    class Meta:
        verbose_name = '教师'

    def __str__(self):
        return self.teacher_id


class Course(models.Model):
    """课程"""
    course_id = models.IntegerField(primary_key=True, verbose_name="课程ID")
    course_name = models.CharField(max_length=30, verbose_name="课程名称")
    teacher = models.OneToOneField(Teacher, related_name='course_teacher', to_field="teacher_id", verbose_name="课程号",
                                   on_delete=models.CASCADE)

    class Meta:
        verbose_name = '课程'

    def __str__(self):
        return self.course_id


class Score(models.Model):
    """分数"""
    course = models.OneToOneField(Course, on_delete=models.CASCADE)
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    score = models.IntegerField(verbose_name='分数')

    class Meta:
        verbose_name = '分数表'

    def __str__(self):
        return self.score

import hashlib
from rest_framework.serializers import ValidationError
from . import models
import re
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
from datetime import datetime
from django.utils import timezone
from rest_framework import serializers
from .models import Student, User, Course, Teacher, Class, Score


class RoleValidator(object):
    """类级别的验证 可以复用"""

    def __init__(self, base):
        self.base = base

    # 执行验证方法
    def __call__(self, value):
        # 例如，此处进行判断
        if value not in [0, 1]:
            # 不满足 则抛出验证错误
            message = '角色只能为0或1 0:老师 1:学生'
            raise serializers.ValidationError(message)


class UserSerializer(serializers.ModelSerializer):
    ROLE_CHOICES = [
        ('0', 'Teacher'),
        ('1', 'Student')
    ]

    user_id = serializers.CharField(required=False, read_only=True)
    role = serializers.ChoiceField(error_messages={'required': 'role must in 0 or 1 0:老师 1:学生'},
                                   choices=ROLE_CHOICES,
                                   required=False, source='get_role_display', default=1)
    last_login = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', required=False)
    password = serializers.CharField(required=False, label='密码', max_length=256, write_only=True)

    def validate_password(self, value):
        """钩子函数的验证"""
        if len(value) < 5:
            message = 'password length is not allow less than 5'
            raise serializers.ValidationError(message)
        return value

    class Meta:
        model = User
        fields = '__all__'
        verbose_name = '用户'
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def create(self, validated_data):
        """重写create方法实现，将密码MD5加密后保存"""
        password = validated_data["password"]
        md5 = hashlib.md5()
        md5.update(password.encode('utf-8'))
        password = md5.hexdigest()

        validated_data['role'] = validated_data.pop("get_role_display")
        validated_data['password'] = password

        user = User.objects.create(**validated_data)

        return user


class StudentSerializer(serializers.ModelSerializer):
    student_id = serializers.CharField(read_only=False)
    class_name_id = serializers.CharField(read_only=False)

    class Meta:
        model = Student
        fields = '__all__'
        verbose_name = '学生'
        depth = 1

    def to_representation(self, instance):
        ret = {
            'id': instance.id,
            'student_id': instance.student.user_id,
            'name': instance.student.name,
            'age': instance.student.age,
            'class_name': instance.class_name.class_name,
        }

        return ret


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = models.User
        fields = ('username', 'password')

    def validate(self, attrs):
        # user_obj = authenticate(**attrs)
        # if not user_obj:
        #     raise ValidationError('用户名或密码错误')

        # 多方式登录
        user = self._many_method_login(**attrs)

        # 通过user对象生成payload载荷
        payload = jwt_payload_handler(user)
        # 通过payload签发token
        token = jwt_encode_handler(payload)

        # 将user和token存放在序列化对象中,方便返回到前端去
        self.user = user
        self.token = token
        return attrs

    # 多方式登录 （用户名、邮箱、手机号三种方式登录）
    def _many_method_login(self, **attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        # 利用正则匹配判断用户输入的信息
        # 1.判断邮箱登录
        if re.match(r'.*@.*', username):
            user = models.User.objects.filter(email=username).first()

        # 2.判断手机号登录
        elif re.match(r'^1[3-9][0-9]{9}$', username):
            user = models.User.objects.filter(mobile=username).first()
        # 3.用户名登录
        else:
            user = models.User.objects.filter(username=username).first()

        if not user:
            raise ValidationError({'username': '账号有误'})

        # 对传入的password进行encode
        md5 = hashlib.md5()
        md5.update(password.encode('utf-8'))
        password = md5.hexdigest()

        if not user.password == password:
            # if not user.check_password(password):
            raise ValidationError({'password': '密码错误'})

        # 更新user表last_login 最后登陆时间
        user.last_login = datetime.now()
        models.User.objects.filter(username=username).update(last_login=timezone.now())
        return user


class ScoreSerializer(serializers.ModelSerializer):
    course_id = serializers.CharField(read_only=False)
    student_id = serializers.CharField(read_only=False)

    class Meta:
        model = Score
        fields = '__all__'
        depth = 1

    def to_representation(self, instance):
        ret = {
            'id': instance.id,
            'course_id': instance.course.course_id,
            'course': instance.course.course_name,
            'student_id': instance.student.student.user_id,
            'name': instance.student.student.name,
            'class_name': instance.student.class_name.class_name,
            'score': instance.score
        }
        return ret


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'
        depth = 2


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'
        depth = 2


class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = '__all__'
        depth = 1

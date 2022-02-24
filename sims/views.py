import py2neo.errors
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Student, User, Course, Teacher, Class, Score
from .serializers import StudentSerializer, UserSerializer, LoginSerializer, \
    CourseSerializer, TeacherSerializer, ClassSerializer, ScoreSerializer
from rest_framework import status
from .pagination import MyPagination
from .permission import TeacherPermission, StudentOnlyReadPermission, StudentOnlyReadOwnPermission
from rest_framework.exceptions import APIException, NotFound

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers


class UserListView(APIView):
    authentication_classes = []
    permission_classes = []

    @method_decorator(cache_page(60 * 60 * 2))
    # @method_decorator(vary_on_headers("Authorization", ))
    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        user_serializer = UserSerializer(users, many=True)
        paginator = MyPagination()
        page_user_list = paginator.paginate_queryset(user_serializer.data,
                                                     self.request, view=self)
        return paginator.get_paginated_response(page_user_list)

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserView(APIView):
    """
    Retrieve, update or delete a user instance.
    """

    permission_classes = [StudentOnlyReadOwnPermission]

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise NotFound("NOT_FOUND")

    def get(self, request, pk, *args, **kwargs):
        user = self.get_object(pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        user = self.get_object(pk)
        user.user_id = pk
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        user = self.get_object(pk)
        data = {"message": "Successfully Delete",
                "user_id": user.user_id,
                "username": user.username}
        user.delete()
        return Response(data, status=status.HTTP_204_NO_CONTENT)


class LoginAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        # print(request.data)
        user_ser = LoginSerializer(data=request.data)
        user_ser.is_valid(raise_exception=True)
        return Response(data={
            'username': user_ser.user.username,
            'token': user_ser.token
        }, status=status.HTTP_200_OK)


class StudentListView(APIView):
    # authentication_classes = []
    permission_classes = [StudentOnlyReadPermission]

    # cache_page 2个小时 60*60*2 s
    # @method_decorator(vary_on_headers("Authorization", ))
    @method_decorator(cache_page(60 * 60 * 2))
    def get(self, request, *args, **kwargs):
        students = Student.objects.all()
        student_serializer = StudentSerializer(instance=students, many=True)
        paginator = MyPagination()
        page_student_list = paginator.paginate_queryset(student_serializer.data, request)
        return paginator.get_paginated_response(page_student_list)

    def post(self, request, *args, **kwargs):
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentView(APIView):
    """
    Retrieve, update or delete a student instance.
    """

    permission_classes = [StudentOnlyReadPermission]

    def get_object(self, pk):
        try:
            return Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            raise NotFound("NOT_FOUND")

    def get(self, request, pk, *args, **kwargs):
        student = self.get_object(pk)
        serializer = StudentSerializer(student)
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        student = self.get_object(pk)
        serializer = StudentSerializer(student, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        student = self.get_object(pk)
        student.delete()
        data = {"message": "Successfully Delete",
                "student_id": student.student_id,
                "class_id": student.class_name_id}

        return Response(data, status=status.HTTP_204_NO_CONTENT)


from rest_framework.generics import GenericAPIView


class CourseView(GenericAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get(self, request, *args, **kwargs):
        course = self.get_object()
        serializer = self.get_serializer(course)
        return Response(serializer.data)


class CourseListView(APIView):
    @method_decorator(cache_page(60 * 60 * 2))
    def get(self, request):
        course = Course.objects.all()
        serializer = CourseSerializer(course, many=True)
        return Response(serializer.data)


from rest_framework import mixins


class TeacherListView(mixins.ListModelMixin, mixins.CreateModelMixin, GenericAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class TeacherView(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  GenericAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = TeacherPermission

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


from rest_framework.viewsets import ViewSet


class ClassViewSet(ViewSet):

    def list(self, request):
        objects = Class.objects.all()
        serializer = ClassSerializer(objects, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            objects = Class.objects.get(class_id=pk)
        except Class.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ClassSerializer(objects)
        return Response(serializer.data)


class ScoreListView(APIView):
    # @method_decorator(cache_page(60 * 60 * 2))
    def get(self, request, *args, **kwargs):
        score = Score.objects.all()
        if request.user.role == "1":
            """如果是学生 就查询自己的成绩"""
            score = Score.objects.filter(student_id=request.user.user_id)
        user_serializer = ScoreSerializer(score, many=True)
        paginator = MyPagination()
        page_user_list = paginator.paginate_queryset(user_serializer.data,
                                                     self.request, view=self)
        return paginator.get_paginated_response(page_user_list)

    def post(self, request, *args, **kwargs):
        serializer = ScoreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ScoreView(APIView):
    permission_classes = [StudentOnlyReadOwnPermission]

    def get_object(self, pk):
        try:
            return Score.objects.get(pk=pk)
        except Score.DoesNotExist:
            raise NotFound("NOT_FOUND")

    def get(self, request, pk, *args, **kwargs):
        student = self.get_object(pk)
        serializer = ScoreSerializer(student)
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        student = self.get_object(pk)
        serializer = ScoreSerializer(student, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        student = self.get_object(pk)
        student.delete()
        data = {"message": "Successfully Delete"}

        return Response(data, status=status.HTTP_204_NO_CONTENT)

from django.core.cache import cache
from django.db.models import Count
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
    ListCreateAPIView
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Project
from .models import Task
from .permissions import IsAdminManager
from .serializers import (
    TaskSerializer,
    ProjectSerializer,
    ProjectDetailSerializer
)
from .task import save_task_to_db


class ProjectListCreateAPIView(ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminManager]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    lookup_field = "id"

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() != "get" and self.request.user.is_manager:
            return self.http_method_not_allowed(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def get_serializer_context(self):
        return {"user": self.request.user}


class ProjectRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminManager]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() != "get" and self.request.user.is_manager:
            return self.http_method_not_allowed(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def get_serializer_context(self):
        return {"user": self.request.user}


class ProjectDetailView(RetrieveAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminManager]
    queryset = Project.objects.prefetch_related('tasks').annotate(
        total_tasks=Count('tasks'),
        completed_tasks=Count('tasks', filter=Q(tasks__status='Completed')),
    )
    serializer_class = ProjectDetailSerializer

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() != "get" and self.request.user.is_manager:
            return self.http_method_not_allowed(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)


class TaskListCreateAPIView(ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    lookup_field = "id"
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_serializer_context(self):
        return {"user": self.request.user}

    def get_queryset(self):
        if self.request.user.is_user:
            return super().get_queryset().filter(
                assigned_to=self.request.user
            )
        return super().get_queryset()


class TaskRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    lookup_field = "id"

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() == "delete" and self.request.user.is_user:
            return self.http_method_not_allowed(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def get_serializer_context(self):
        return {"user": self.request.user}

    def get_object(self):
        task = super().get_object()
        if task.assigned_to != self.request.user:
            raise Http404("You don't have permission to access this task")

        return task


class ApproveTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, task_id):
        user = request.user

        # Check user's role (optional, modify based on your role structure)
        if user.role != 'Manager':  # Assuming user role is stored in a field
            return Response({'error': 'You do not have permission to approve tasks.'}, status=403)

        # Get the task object
        task = get_object_or_404(Task, id=task_id)

        if task.status != 'Pending Approval':
            return Response({'error': 'This task cannot be approved as it is not pending approval.'}, status=400)

        # Temporarily save task data in Redis
        task_data = {
            'title': task.title,
            'description': task.description,
            'status': task.status,
            'created_at': str(task.created_at)
        }
        cache.set(f'task:{task_id}', task_data, timeout=300)  # Store in Redis for 5 minutes

        # Update task status to approved
        task.status = 'Approved'
        task.save()

        # Schedule the Celery task to save the task in the main database after 5 minutes
        save_task_to_db.apply_async((task.id,), countdown=300)  # 5-minute delay

        return Response({'message': 'Task has been approved and will be saved in 5 minutes.'}, status=200)


class RevokeApprovalView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, task_id):
        # Get the task object
        task = get_object_or_404(Task, id=task_id)

        # Check if the task is approved
        if task.status != 'Approved':
            return Response({'error': 'This task cannot be revoked as it is not approved.'}, status=400)

        # Revoke approval (set status back to "Pending Approval")
        task.status = 'Pending Approval'
        task.save()

        # Remove the task from Redis if it is cached
        cache_key = f'task:{task_id}'
        if cache.get(cache_key):
            cache.delete(cache_key)

        return Response({'message': 'Task approval has been revoked and will not be saved to the database.'},
                        status=200)


class PendingTasksView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user
        # Check if the user is a manager
        if user.role != 'Manager':
            return Task.objects.none()  # Return no tasks if the user is not a manager

        # Return tasks with "Pending Approval" status
        return Task.objects.filter(status='Pending Approval')

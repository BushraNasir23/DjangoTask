from rest_framework import serializers

from account.serializers import UserRegistrationSerializer
from .models import Task, Project
from django.utils.timezone import now


class TaskSerializer(serializers.ModelSerializer):
    created_by = UserRegistrationSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "due_date",
            "priority",
            "status",
            "project",
            "assigned_to",
            "created_at",
            "updated_at",
            "created_by",
        ]

        read_only_fields = [
            "id",
            "created_by"
        ]

    def validate_due_date(self, value):
        if value <= now():
            raise serializers.ValidationError("The due date must be in the future.")
        return value

    def validate_project(self, value):
        if not Project.objects.filter(pk=value.id).exists():
            raise serializers.ValidationError(f"Invalid pk \"{value.id}\" - object does not exist.")
        return value

    def create(self, validated_data):
        user = self.context["user"]
        status = validated_data.pop("status")
        if user.is_user and status != "In Progress":
            task = Task(**validated_data, created_by=user)
        else:
            task = Task(**validated_data, created_by=user, status=status)
        task.save()
        return task

    def update(self, instance, validated_data):
        user = self.context["user"]
        status = validated_data.pop("status")
        if user.is_user and status != "In Progress":
            raise serializers.ValidationError({
                "status": "As a regular user, you can only update tasks to 'In Progress'."
            })

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if status:
            instance.status = status

        instance.save()

        return instance


class ProjectSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    created_by = UserRegistrationSerializer(read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "created_at",
            "created_by",
            "tasks",
            "total_tasks",
            "completed_tasks"
        ]

        read_only_fields = [
            "id",
            "created_by"
        ]

    def create(self, validated_data):
        project = Project(**validated_data, created_by=self.context["user"])
        project.save()
        return project


class ProjectDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    created_at = serializers.DateTimeField()
    created_by = UserRegistrationSerializer(read_only=True)
    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "created_at",
            "created_by",
            "total_tasks",
            "completed_tasks"
        ]

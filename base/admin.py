from django.contrib import admin
from .models import Project, Task


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'created_by', 'created_at')
    list_filter = ('created_at', 'created_by')  # Filters for quick access
    search_fields = ('name', 'description')  # Search by name or description
    ordering = ('-created_at',)  # Order by most recen


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'priority', 'status', 'project', 'assigned_to', 'due_date', 'created_at')
    list_filter = ('priority', 'status', 'project', 'due_date')  # Add filters
    search_fields = ('title', 'description', 'assigned_to__username', 'project__name')  # Allow searching by relationships
    ordering = ('-due_date',)  # Order by the nearest due dat
    fieldsets = (  # Organize fields into sections
        ('Basic Information', {
            'fields': ('title', 'description', 'priority', 'status', 'project','created_by')
        }),
        ('Assignment', {
            'fields': ('assigned_to', 'due_date')
        }),
       
    )





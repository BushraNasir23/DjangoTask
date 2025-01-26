from django import forms
from .models import Task, UserProfile
from django.core.exceptions import ValidationError
from django.utils import timezone

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'priority', 'status', 'project', 'assigned_to']
    
    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        # Dynamically populate the 'assigned_to' field with active users (Optional)
        self.fields['assigned_to'].queryset = UserProfile.objects.all()
    
    # Business Logic for validating due_date
    def clean_due_date(self):
        due_date = self.cleaned_data['due_date']
        if due_date < timezone.now():
            raise ValidationError('The due date cannot be in the past.')
        return due_date

    # Business Logic for updating task status
    def clean_status(self):
        status = self.cleaned_data['status']
        user = self.instance.assigned_to.user if self.instance else None
        
        # Ensure that only a Manager can mark a task as "Completed"
        if status == 'Completed' and (user is None or user.profile.role != 'Manager'):
            raise ValidationError('Only a Manager can mark a task as Completed.')
        
        return status









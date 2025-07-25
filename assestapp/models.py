from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Employee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    empId = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    date = models.DateTimeField(auto_now_add=True)
    phone=models.CharField(max_length=10,default=True,null=True)
    status=models.CharField(max_length=8,default='Active')
    
    def __str__(self):
        return self.user.username

class Details(models.Model):
    itemid = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)
    modelno = models.CharField(max_length=100)
    make = models.CharField(max_length=100)
    description=models.TextField(null="")
    units = models.CharField(max_length=50,default="numbers")

    def __str__(self):
        return self.description

class Assigned(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    details = models.ForeignKey(Details, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

# class ProductAssigned(models.Model):
#     make = models.CharField(max_length=100)
#     modelno = models.CharField(max_length=100)
#     description = models.TextField()
#     units = models.CharField(max_length=100)
#     assigned_date = models.DateField(default=timezone.now)
#     employee = models.ForeignKey('Employee', on_delete=models.CASCADE,null=True,blank=True)

#     def assigned_text(self):
#         today = timezone.now().date()
#         yesterday = today - timezone.timedelta(days=1)
#         if self.assigned_date == today:
#             return "Today"
#         elif self.assigned_date == yesterday:
#             return "Yesterday"
#         else:
#             return self.assigned_date.strftime("%d %b %Y")

#         if self.employee:
#             return f"Assigned to {self.employee.name} on {date_str}"
#         return f"Assigned on {date_str}"
#     assigned_text.short_description = 'Assigned'

#     def __str__(self):
#         return f"{self.make} - {self.modelno}"

# class ProductAssigned(models.Model):
#     make = models.CharField(max_length=100)
#     modelno = models.CharField(max_length=100)
#     description = models.TextField()
#     units = models.CharField(max_length=100)
#     assigned_date = models.DateField(default=timezone.now)
#     employee = models.ForeignKey('Employee', on_delete=models.CASCADE, null=True, blank=True)

#     def assigned_text(self):
#         today = timezone.now().date()
#         yesterday = today - timezone.timedelta(days=1)
#         if self.assigned_date == today:
#             return "Today"
#         elif self.assigned_date == yesterday:
#             return "Yesterday"
#         else:
#             return self.assigned_date.strftime("%d %b %Y")

#         if self.employee:
#             return f"Assigned to {self.employee.user.username} on {self.assigned_date.strftime('%d %b %Y')}"
#         return f"Assigned on {self.assigned_date.strftime('%d %b %Y')}"

#     assigned_text.short_description = 'Assigned'

#     def __str__(self):
#         return f"{self.make} - {self.modelno}"


class ProductAssigned(models.Model):
    make = models.CharField(max_length=100)
    modelno = models.CharField(max_length=100)
    description = models.TextField()
    units = models.CharField(max_length=100)
    assigned_date = models.DateField(default=timezone.now)
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, null=True, blank=True)

    def assigned_text(self):
        """Returns a human-readable assignment status."""
        today = timezone.now().date()
        yesterday = today - timezone.timedelta(days=1)

        # Determine the assignment date label
        if self.assigned_date == today:
            date_str = "Today"
        elif self.assigned_date == yesterday:
            date_str = "Yesterday"
        else:
            date_str = self.assigned_date.strftime("%d %b %Y")

        # Include employee's username if assigned
        if self.employee:
            return f"Assigned to {self.employee.user.username} on {date_str}"
        return f"Assigned on {date_str}"

    assigned_text.short_description = 'Assigned'

    def __str__(self):
        return f"{self.make} - {self.modelno}"

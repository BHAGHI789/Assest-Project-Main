from pdb import set_trace

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string

from .models import Employee
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import never_cache
from django.shortcuts import render,redirect,HttpResponse
from django.contrib import messages
from django.http import JsonResponse
from .models import Details
from .models import Assigned
from django.db.models import Q
from datetime import date,timedelta, datetime as dt
from django.utils.timezone import make_aware
from django.utils.timezone import now, timedelta
from django.views.decorators.csrf import csrf_exempt,ensure_csrf_cookie
import json
from django.views.decorators.http import require_POST
from datetime import * 
import pandas as pd
# Bhagyaraj Developed
def reg(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('pass1')
        phoneno = request.POST.get('phoneNo')
        my_user = User.objects.create_user(uname, email, password)
        my_user.save()

        empId = request.POST.get('empId')
        gender = request.POST.get('gender')
        Employee.objects.create(user=my_user, empId=empId, gender=gender, phone=phoneno)

        return redirect('login')

    return render(request, "REGISTRATION_FORM.html")
def log(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                emp = Employee.objects.get(user=user)
                if emp.status == 'Inactive':
                    return render(request, "login1.html", {
                        'error': 'Your account is deactivated. Please contact the admin.'
                    })
                else:
                    login(request, user)
                    return redirect('dashboard')
            except Employee.DoesNotExist:
                return render(request, "login1.html", {
                    'error': 'Employee profile not found.'
                })
        else:
            return render(request, "login1.html", {
                'error': 'Invalid username or password.'
            })

    return render(request, "login1.html")

@login_required(login_url='/log/')
@never_cache
def db(request):
    return render(request, 'dashboard.html')

@login_required(login_url='/log/')
def product(request):
    if request.method == "POST":
        record_id = request.POST.get('record_id')
        make = request.POST.get('make')
        modelno = request.POST.get('modelno')
        description = request.POST.get('description')
        units = request.POST.get("unit", "")

        if record_id:
            try:
                obj = Details.objects.get(id=record_id)
                obj.make = make
                obj.modelno = modelno
                obj.description = description
                obj.units = units
                obj.save()
                messages.success(request, 'Record updated successfully!')
            except Details.DoesNotExist:
                messages.error(request, 'Record not found.')
        else:
            Details.objects.create(
                make=make,
                modelno=modelno,
                description=description,
                units = units
            )
            messages.success(request, 'Record created successfully!')

    data = Details.objects.all()
    return render(request, 'product.html', {'data': data})


def delete_product(request, pk):
    if request.method == 'POST':
        try:
            Details.objects.get(pk=pk).delete()
            return JsonResponse({'success': True})
        except Details.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required(login_url='/log/')
def producttable(request):
    employees = Employee.objects.all()
    return render(request, 'producttable.html', {'employees': employees})

@login_required(login_url='/log/')
def logout_view(request):
    logout(request)
    return redirect('login')

def toggle_user_status(request, empId):
    if request.method == 'POST':
        try:
            emp = get_object_or_404(Employee, empId=empId)
            emp.status = 'Inactive' if emp.status == 'Active' else 'Active'
            emp.save()
            return JsonResponse({'status': emp.status})
        except Employee.DoesNotExist:
            return JsonResponse({'error': 'Employee not found'}, status=404)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required(login_url='/log/')
def filter(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        # Search Assigned objects where related product's 'make' contains the query (case-insensitive)
        results = Assigned.objects.filter(
            employee__user__username__icontains=query
        ).select_related('employee', 'details').order_by('-date')
    else:
        # Optionally show all assigned products if no query given
        results = Assigned.objects.select_related('employee', 'details').order_by('-date')

    return render(request, 'filters.html', {
        'query': query,
        'results': results,
    })

def assigned_view(request):
    message = ""

    if request.method == "POST":
        product_id = request.POST.get('product')
        user_id = request.POST.get('users')

        try:
            details = Details.objects.get(id=product_id)
            employee = Employee.objects.get(id=user_id)

            Assigned.objects.create(employee=employee, details=details)
            message = "Assignment successful!"
        except Details.DoesNotExist:
            message = "Product not found."
        except Employee.DoesNotExist:
            message = "User not found."

    products = Details.objects.all()
    users = Employee.objects.all()
    assignments = Assigned.objects.select_related('employee', 'details').order_by('-date')

    return render(request, 'assigned.html', {
        'products': products,
        'users': users,
        'assignments': assignments,
        'message': message
    })



@login_required(login_url='/log/')
def productfilter(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        results = Assigned.objects.filter(
            details__description__icontains=query
        ).select_related('employee', 'details').order_by('-date')
    else:
        results = Assigned.objects.select_related('employee', 'details').order_by('-date')

    return render(request, 'productfilter.html', {
        'query': query,
        'results': results,
    })

def dashboard(request):
    #import pdb;pdb.set_trace()
    today = now().date()
    yesterday = today - timedelta(days=1)

    assigned_data = Assigned.objects.filter(
        date__date__in=[today, yesterday]
    ).select_related('employee', 'details')

    # Prepare data for table
    assigned_display = []
    for assign in assigned_data:
        assigned_display.append({
            'make': assign.details.make,
            'modelno': assign.details.modelno,
            'description': assign.details.description,
            'units': assign.details.units,
            'assigned_text': f"Assigned to {assign.employee.user.first_name or assign.employee.user.username} {'today' if assign.date.date() == today else 'yesterday'}"
        })

    context = {
        'assigned_data': assigned_display,
        'total_products': Details.objects.count(),
        'total_users': Employee.objects.count(),
        'latest_users': User.objects.order_by('-last_login')[:5],
    }
    return render(request, 'dashboard.html', context)


@csrf_exempt
def handle_ajax(request):
    
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        import pdb;pdb.set_trace()
        try:
            data = json.loads(request.body.decode('utf-8'))
            record_id = data.get("formdata")["record_id"]
            if data.get("formdata")["status"]=="New":
                my_record=Details()
                my_record.date=datetime.now()
                my_record.make = data.get("formdata")["make"]
                my_record.modelno = data.get("formdata")["modelno"]
                my_record.description = data.get("formdata")["description"]
                my_record.units = data.get("formdata")["units"]
                my_record.save()
                updatedoradd="New"
            elif data.get("formdata")["status"]=="updated":
                Update_reocrd=Details.objects.get(id=record_id)
                Update_reocrd.date=datetime.now()
                Update_reocrd.make = data.get("formdata")["make"]
                Update_reocrd.modelno = data.get("formdata")["modelno"]
                Update_reocrd.description = data.get("formdata")["description"]
                Update_reocrd.units = data.get("formdata")["units"]
                Update_reocrd.save()
                updatedoradd="Updated"
            elif data.get("formdata")["status"]=="Deleted":
                Details.objects.get(id=record_id).delete()
                updatedoradd="Deleted"
            records=pd.DataFrame(Details.objects.all().values("id","itemid","date","modelno","make","units","description")).to_dict("records")
            return JsonResponse({'success': True,"records":records,"checking":updatedoradd})
        except json.JSONDecodeError as e:
            print("JSON error:", str(e))
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    elif request.method == 'GET':
        assets = Details.objects.all().order_by('-id')
        return render(request, 'ajaxs.html', {'data': assets})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'})


# @csrf_exempt
# def delete_ajax(request, record_id):
#     if request.method == 'POST':
#         import pdb;pdb.set_trace()
#         try:
#             data = json.loads(request.body.decode('utf-8'))
#             record_id = data.get("formdata")["record_id"]
#             asset = Details.objects.get(id=record_id)
#             asset.delete()
#             return JsonResponse({'success': True, 'message': 'Product deleted successfully!'})
#         except:
#             print("JSON error:", str(e))
#             return JsonResponse({"error": "Invalid JSON"}, status=400)
#     return JsonResponse({'success': False, 'message': 'Invalid request'})

# def save_product_ajax(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)#Reads the raw body of the request (which is expected to be JSON) and parses it into a Python dictionary using json.loads(). This is how you retrieve data sent via JavaScript's fetch() or XMLHttpRequest().
#         record_id = data.get('record_id')
#         make = data.get('make')
#         modelno = data.get('modelno')
#         description = data.get('description')
#         unit = data.get('unit')
#
#         if not all([make, modelno, description, unit]):
#             return JsonResponse({'success': False, 'error': 'Missing fields.'})
#
#         if record_id:
#             product = Details.objects.get(id=record_id)
#         else:
#             product = Details()
#
#         product.make = make
#         product.modelno = modelno
#         product.description = description
#         product.units = unit
#         product.save()
#
#         return JsonResponse({'success': True, 'record': {
#             'id': product.id,
#             'make': product.make,
#             'modelno': product.modelno,
#             'description': product.description,
#             'units': product.units
#         }})
#     data = Details.objects.all()
#     return render(request,'Ajax.html',{'data':data})
#     #return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)
#
# def delete_product_ajax(request, pk):
#     if request.method == 'POST':
#         try:
#             Details.objects.get(pk=pk).delete()
#             return JsonResponse({'success': True})
#         except Details.DoesNotExist:
#             return JsonResponse({'success': False, 'error': 'Not found'})
#     return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)
#     #return render(request,'Ajax.html')

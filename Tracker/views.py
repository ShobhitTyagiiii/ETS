from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.db import IntegrityError
from django.http import JsonResponse, FileResponse, HttpResponse
from django.db.models import Sum
from django.contrib import messages

from django.utils.timezone import now
from calendar import month_name
import datetime
import os
import io
import re

from openpyxl import Workbook
from reportlab.pdfgen import canvas

from .models import Expense

User = get_user_model()


# --- ADD EXPENSE ---

from django.utils.timezone import now

@login_required
def add_expense_view(request):
    if request.method == 'POST':
        title = request.POST['title']
        amount = request.POST['amount']
        category = request.POST['category']
        description = request.POST.get('description', '')
        date = request.POST.get('date')
        invoice = request.FILES.get('invoice')

        if not date:
            date = now().date()

        Expense.objects.create(
            user=request.user,
            title=title,
            amount=amount,
            category=category,
            description=description,
            date=date,
            invoice=invoice
        )

        return redirect('/add-expense?submitted=true')

    submitted = request.GET.get('submitted') == 'true'
    return render(request, 'add_expense.html', {
        'submitted': submitted,
        'today': now().date().isoformat()
    })


# --- EDIT EXPENSE ---
@login_required
def edit_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)

    if request.method == 'POST':
        expense.title = request.POST.get('title')
        expense.amount = request.POST.get('amount')
        expense.category = request.POST.get('category')
        expense.date = request.POST.get('date')

        if 'delete_invoice' in request.POST and expense.invoice:
            if os.path.isfile(expense.invoice.path):
                os.remove(expense.invoice.path)
            expense.invoice = None

        if request.FILES.get('invoice'):
            expense.invoice = request.FILES['invoice']

        expense.save()
        messages.success(request, "Expense updated successfully.")
        return redirect('my_submissions')

    return render(request, 'edit_expense.html', {'expense': expense})


# --- DELETE EXPENSE ---
@login_required
def delete_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)
    if expense.invoice and os.path.isfile(expense.invoice.path):
        os.remove(expense.invoice.path)
    expense.delete()
    messages.success(request, "Expense deleted.")
    return redirect('my_submissions')


# --- MY SUBMISSIONS ---
@login_required
def my_submissions_view(request):
    user_expenses = Expense.objects.filter(user=request.user).order_by('-date')
    return render(request, 'my_submissions.html', {'expenses': user_expenses})


# --- LOGIN + REGISTER ---
@csrf_protect
def login_register_view(request):
    login_error = False
    register_failed = False
    form_data = {}

    if request.method == "POST":
        # --- Login Form ---
        if 'email' in request.POST and 'password' in request.POST and 'first_name' not in request.POST:
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                request.session.set_expiry(1800)
                return redirect('dashboard')
            else:
                login_error = True
                messages.error(request, "Invalid email or password.")

        # --- Registration Form ---
        elif 'first_name' in request.POST:
            form_data = {
                'first_name': request.POST.get('first_name', ''),
                'last_name': request.POST.get('last_name', ''),
                'email': request.POST.get('email', ''),
                'role': request.POST.get('role', ''),
            }

            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

            # Password Validation
            if password1 != password2:
                messages.error(request, "Passwords do not match.")
                register_failed = True
            elif len(password1) < 8:
                messages.error(request, "Password must be at least 8 characters long.")
                register_failed = True
            elif not any(char.isdigit() for char in password1):
                messages.error(request, "Password must contain at least one digit.")
                register_failed = True
            elif not any(char.isalpha() for char in password1):
                messages.error(request, "Password must contain at least one letter.")
                register_failed = True
            elif not re.search(r'[!@#$%^&*(),.?":{}|<>]', password1):
                messages.error(request, "Password must contain at least one special character.")
                register_failed = True
            elif User.objects.filter(email=form_data['email']).exists():
                messages.error(request, "Email already exists.")
                register_failed = True
            else:
                try:
                    user = User.objects.create_user(
                        email=form_data['email'],
                        password=password1,
                        first_name=form_data['first_name'],
                        last_name=form_data['last_name'],
                        role=form_data['role']
                    )
                    messages.success(request, "Registration successful! Please log in.")
                    return redirect('/')  # Redirect to login after successful registration
                except IntegrityError:
                    messages.error(request, "An error occurred during registration.")
                    register_failed = True

    return render(request, "login_register.html", {
        "login_error": login_error,
        "register_failed": register_failed,
        "form_data": form_data
    })


# --- DASHBOARD VIEW ---
@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html')


# --- CHART DATA API ---
@login_required
@require_http_methods(["GET"])
def chart_data_api(request):
    today = now().date()
    monthly_totals = [0] * 12
    expenses = Expense.objects.filter(user=request.user, date__year=today.year)
    for exp in expenses:
        monthly_totals[exp.date.month - 1] += float(exp.amount)

    month_labels = [month_name[i][:3] for i in range(1, 13)]

    category_data = (
        expenses.values('category')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )
    category_labels = [entry['category'] for entry in category_data]
    category_totals = [float(entry['total']) for entry in category_data]

    return JsonResponse({
        'month_labels': month_labels,
        'monthly_totals': monthly_totals,
        'category_labels': category_labels,
        'category_totals': category_totals,
    })


@login_required
@require_http_methods(["GET"])
def reports_chart_data_api(request):
    range_type = request.GET.get('range', 'daily').lower()
    expenses = filter_expenses(request.user, range_type)

    category_data = expenses.values('category').annotate(total=Sum('amount')).order_by('-total')

    return JsonResponse({
        'category_labels': [entry['category'] for entry in category_data],
        'category_totals': [float(entry['total']) for entry in category_data],
        'range_type': range_type
    })


# --- FILTER UTILITY ---
def filter_expenses(user, range_type):
    today = now().date()
    if range_type == 'daily':
        start_date = today
    elif range_type == 'weekly':
        start_date = today - datetime.timedelta(days=7)
    elif range_type == 'quarterly':
        start_date = today - datetime.timedelta(days=90)
    elif range_type == 'half_yearly':
        start_date = today - datetime.timedelta(days=180)
    else:
        start_date = today - datetime.timedelta(days=365)

    return Expense.objects.filter(user=user, date__gte=start_date)


# --- REPORT VIEW ---
@login_required
def reports_view(request):
    if request.method == 'POST':
        range_type = request.POST.get('range', 'daily').lower()
        format_type = request.POST.get('format', 'html')
        expenses = filter_expenses(request.user, range_type)

        if format_type == 'pdf':
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer)
            p.drawString(100, 800, f"{range_type.capitalize()} Expense Report")
            y = 750
            for expense in expenses:
                p.drawString(100, y, f"{expense.date} - {expense.category} - ₹{expense.amount}")
                y -= 20
            p.showPage()
            p.save()
            buffer.seek(0)
            return FileResponse(buffer, as_attachment=True, filename=f'{range_type}_report.pdf')

        elif format_type == 'excel':
            wb = Workbook()
            ws = wb.active
            ws.append(['Date', 'Category', 'Amount'])
            for expense in expenses:
                ws.append([expense.date.strftime("%Y-%m-%d"), expense.category, expense.amount])
            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = f'attachment; filename="{range_type}_report.xlsx"'
            wb.save(response)
            return response

        category_data = expenses.values('category').annotate(total=Sum('amount')).order_by('-total')
        return render(request, 'reports.html', {
            'category_data': category_data,
            'range_type': range_type
        })

    return render(request, 'reports.html')


# --- EXPENSE APPROVAL PAGE ---
@login_required
def approve_expenses_view(request):
    return render(request, 'approve_expenses.html')


# --- LOGOUT VIEW ---
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


# --- TEST API ---
@login_required
@require_http_methods(["GET"])
def test_api(request):
    return JsonResponse({
        'status': 'success',
        'message': 'API is working',
        'user': request.user.email,
        'timestamp': now().isoformat()
    })
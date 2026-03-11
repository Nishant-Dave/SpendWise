"""
Views for the SpendWise expenses app.

Sections:
  1. Authentication  – register, login, logout
  2. Dashboard       – summary statistics
  3. Category        – list, create
  4. Transaction     – list (with filters), create, update, delete, detail
  5. Settings        – profile, account deletion
  6. Analytics       – CSV export, chart JSON API
"""

import csv
import json
from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CategoryForm, RegisterForm, TransactionForm
from .models import Category, Transaction


# ===========================================================================
# 1.  AUTHENTICATION
# ===========================================================================

def register_view(request):
    """Create a new user account and immediately log them in."""
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f'Welcome to SpendWise, {user.username}! 🎉',
            )
            return redirect('/')
    else:
        form = RegisterForm()

    return render(request, 'expenses/register.html', {'form': form})


def login_view(request):
    """Authenticate an existing user and redirect to dashboard."""
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Honour ?next= redirect param if present
            next_url = request.GET.get('next') or request.POST.get('next') or '/'
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'expenses/login.html', {
        'next': request.GET.get('next', ''),
    })


def logout_view(request):
    """Log out the current user and redirect to the login page."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('/login/')


# ===========================================================================
# 2.  DASHBOARD
# ===========================================================================

@login_required
def dashboard_view(request):
    """
    Landing page after login.

    Computes headline KPIs for the current calendar month:
      - Total income
      - Total expenses
      - Net balance
      - 5 most recent transactions

    The bar chart data for togglable time ranges will be added in Part 3.
    """
    today = timezone.localdate()
    current_month_qs = Transaction.objects.filter(
        user=request.user,
        date__year=today.year,
        date__month=today.month,
    )

    total_income = (
        current_month_qs.filter(type=Transaction.INCOME)
        .aggregate(total=Sum('amount'))['total']
        or Decimal('0.00')
    )
    total_expense = (
        current_month_qs.filter(type=Transaction.EXPENSE)
        .aggregate(total=Sum('amount'))['total']
        or Decimal('0.00')
    )
    net_balance = total_income - total_expense

    recent_transactions = (
        Transaction.objects.filter(user=request.user)
        .select_related('category')
        .order_by('-date', '-id')[:5]
    )

    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'net_balance': net_balance,
        'recent_transactions': recent_transactions,
        'current_month': today.strftime('%B %Y'),
    }
    return render(request, 'expenses/dashboard.html', context)


# ===========================================================================
# 3.  CATEGORIES
# ===========================================================================

@login_required
def category_list_view(request):
    """Display all categories belonging to the logged-in user."""
    categories = Category.objects.filter(user=request.user)
    return render(request, 'expenses/category_list.html', {
        'categories': categories,
    })


@login_required
def category_create_view(request):
    """Create a new category for the logged-in user."""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            try:
                category.save()
                messages.success(
                    request,
                    f'{category.emoji} Category "{category.name}" created!',
                )
                return redirect('category_create')
            except Exception:
                # unique_together violation: name already exists for this user
                form.add_error(
                    'name',
                    'You already have a category with this name.',
                )
    else:
        form = CategoryForm()

    return render(request, 'expenses/category_form.html', {
        'form': form,
        'form_title': 'Add Category',
    })


@login_required
def category_delete_view(request, pk):
    """Delete a category owned by the logged-in user."""
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        category_name = str(category)
        category.delete()
        messages.success(request, f'Category "{category_name}" deleted.')
        return redirect('/categories/')
    return render(request, 'expenses/category_confirm_delete.html', {
        'object': category,
        'object_type': 'Category',
        'cancel_url': 'category_list',
    })


# ===========================================================================
# 4.  TRANSACTIONS  (CRUD)
# ===========================================================================

@login_required
def transaction_list_view(request):
    """
    List all transactions for the current user with optional filters:
      - ?type=Income|Expense
      - ?category=<pk>
      - ?date_from=YYYY-MM-DD
      - ?date_to=YYYY-MM-DD

    Also computes filtered totals for income and expense.
    """
    qs = (
        Transaction.objects.filter(user=request.user)
        .select_related('category')
        .order_by('-date', '-id')
    )

    # ---------- filters ----------
    filter_type = request.GET.get('type', '')
    filter_category = request.GET.get('category', '')
    filter_date_from = request.GET.get('date_from', '')
    filter_date_to = request.GET.get('date_to', '')

    if filter_type in (Transaction.INCOME, Transaction.EXPENSE):
        qs = qs.filter(type=filter_type)

    if filter_category:
        qs = qs.filter(category__pk=filter_category)

    if filter_date_from:
        qs = qs.filter(date__gte=filter_date_from)

    if filter_date_to:
        qs = qs.filter(date__lte=filter_date_to)
    # --------------------------------

    total_income = (
        qs.filter(type=Transaction.INCOME)
        .aggregate(total=Sum('amount'))['total']
        or Decimal('0.00')
    )
    total_expense = (
        qs.filter(type=Transaction.EXPENSE)
        .aggregate(total=Sum('amount'))['total']
        or Decimal('0.00')
    )

    user_categories = Category.objects.filter(user=request.user)

    context = {
        'transactions': qs,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_balance': total_income - total_expense,
        'user_categories': user_categories,
        # Pass filter values back for form persistence
        'filter_type': filter_type,
        'filter_category': filter_category,
        'filter_date_from': filter_date_from,
        'filter_date_to': filter_date_to,
    }
    return render(request, 'expenses/transaction_list.html', context)


@login_required
def transaction_detail_view(request, pk):
    """View a single transaction (read-only detail page)."""
    transaction = get_object_or_404(
        Transaction.objects.select_related('category'),
        pk=pk,
        user=request.user,
    )
    return render(request, 'expenses/transaction_detail.html', {
        'transaction': transaction,
    })


@login_required
def transaction_create_view(request):
    """Create a new transaction for the logged-in user."""
    if request.method == 'POST':
        form = TransactionForm(user=request.user, data=request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(
                request,
                f'Transaction of ₹{transaction.amount} added successfully!',
            )
            return redirect('transaction_create')
    else:
        form = TransactionForm(user=request.user)

    return render(request, 'expenses/transaction_form.html', {
        'form': form,
        'form_title': 'Add Transaction',
    })


@login_required
def transaction_update_view(request, pk):
    """Edit an existing transaction owned by the logged-in user."""
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    if request.method == 'POST':
        form = TransactionForm(
            user=request.user,
            data=request.POST,
            instance=transaction,
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction updated.')
            return redirect('/transactions/')
    else:
        form = TransactionForm(user=request.user, instance=transaction)

    return render(request, 'expenses/transaction_form.html', {
        'form': form,
        'form_title': 'Edit Transaction',
        'transaction': transaction,
    })


@login_required
def transaction_delete_view(request, pk):
    """Delete a transaction owned by the logged-in user."""
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Transaction deleted.')
        return redirect('/transactions/')

    return render(request, 'expenses/transaction_confirm_delete.html', {
        'object': transaction,
        'object_type': 'Transaction',
        'cancel_url': 'transaction_list',
    })


# ===========================================================================
# 5.  SETTINGS
# ===========================================================================

@login_required
def settings_view(request):
    """
    Settings page: displays user profile information and provides a
    Danger Zone form for secure account deletion.

    On POST the user must supply their current password.  We verify it
    with check_password() before permanently deleting the account.
    """
    error = None

    if request.method == 'POST':
        password = request.POST.get('password', '')
        if request.user.check_password(password):
            # Password correct — delete account and redirect to register
            request.user.delete()
            messages.success(
                request,
                'Your account has been permanently deleted.',
            )
            return redirect('register')
        else:
            error = 'Incorrect password. Please try again.'

    return render(request, 'expenses/settings.html', {
        'error': error,
        'page_user': request.user,
    })


# ===========================================================================
# 6.  ANALYTICS
# ===========================================================================

@login_required
def export_transactions_csv(request):
    """
    Download all transactions for the logged-in user as a CSV file.

    Columns: Date, Category, Description, Type, Amount
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="spendwise_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Category', 'Description', 'Type', 'Amount (INR)'])

    transactions = (
        Transaction.objects
        .filter(user=request.user)
        .select_related('category')
        .order_by('-date', '-id')
    )

    for tx in transactions:
        category_label = (
            f'{tx.category.emoji} {tx.category.name}'
            if tx.category else 'No Category'
        )
        writer.writerow([
            tx.date.strftime('%Y-%m-%d'),
            category_label,
            tx.description or '',
            tx.type,
            tx.amount,
        ])

    return response


@login_required
def dashboard_chart_data(request):
    """
    JSON API for the dashboard spending overview chart.

    Query param: ?range=1_month | 3_months | 6_months  (default: 1_month)

    For 1_month  → daily aggregation for the current calendar month.
    For 3_months / 6_months → monthly aggregation.

    Response shape:
    {
      "labels": ["Jan", "Feb", ...],
      "income":  [1000, 2000, ...],
      "expense": [500,  1500, ...]
    }
    """
    range_param = request.GET.get('range', '1_month')
    today = timezone.localdate()

    # ── Determine window start date ──────────────────────────────────────────
    if range_param == '6_months':
        n_months = 6
    elif range_param == '3_months':
        n_months = 3
    else:
        n_months = 1  # 1_month → daily breakdown

    # ── 1-month view: group by day ───────────────────────────────────────────
    if n_months == 1:
        # First day of the current month
        start = today.replace(day=1)
        qs = (
            Transaction.objects
            .filter(user=request.user, date__gte=start, date__lte=today)
            .order_by('date')
        )

        # Build day → income/expense maps
        income_map: dict[date, Decimal] = {}
        expense_map: dict[date, Decimal] = {}
        for tx in qs:
            if tx.type == Transaction.INCOME:
                income_map[tx.date] = income_map.get(tx.date, Decimal('0')) + tx.amount
            else:
                expense_map[tx.date] = expense_map.get(tx.date, Decimal('0')) + tx.amount

        # All days in the month so far
        all_days: list[date] = []
        d = start
        from datetime import timedelta
        while d <= today:
            all_days.append(d)
            d += timedelta(days=1)

        import calendar as _cal
        labels  = [f'{d.day} {_cal.month_abbr[d.month]}' for d in all_days]
        income  = [float(income_map.get(d, Decimal('0')))  for d in all_days]
        expense = [float(expense_map.get(d, Decimal('0'))) for d in all_days]

    # ── Multi-month view: group by month ─────────────────────────────────────
    else:
        # Start = first day of the month, n_months ago
        # E.g. for 3_months: Jan, Feb, Mar (if today is March)
        year  = today.year
        month = today.month
        months: list[tuple[int, int]] = []  # (year, month) in ascending order
        for i in range(n_months - 1, -1, -1):
            m = month - i
            y = year
            while m <= 0:
                m += 12
                y -= 1
            months.append((y, m))

        start = date(months[0][0], months[0][1], 1)

        qs = (
            Transaction.objects
            .filter(user=request.user, date__gte=start, date__lte=today)
            .annotate(month=TruncMonth('date'))
            .values('month', 'type')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )

        # Build (year, month) → income/expense maps
        income_map2: dict[tuple[int, int], Decimal] = {}
        expense_map2: dict[tuple[int, int], Decimal] = {}
        for row in qs:
            key = (row['month'].year, row['month'].month)
            if row['type'] == Transaction.INCOME:
                income_map2[key] = row['total']
            else:
                expense_map2[key] = row['total']

        import calendar
        labels  = [calendar.month_abbr[m] for _, m in months]
        income  = [float(income_map2.get(key, Decimal('0')))  for key in months]
        expense = [float(expense_map2.get(key, Decimal('0'))) for key in months]

    return JsonResponse({'labels': labels, 'income': income, 'expense': expense})


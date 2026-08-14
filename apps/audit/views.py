from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from apps.accounts.decorators import main_admin_required
from apps.audit.models import AuditLog

@main_admin_required
def audit_logs_list_view(request):
    """
    MAIN ADMIN EXCLUSIVE AUDIT LOG VIEWER
    Strictly restricted to Main Admin. Managers and Customers receive 403 Forbidden.
    """
    logs = AuditLog.objects.all().select_related('actor').order_by('-timestamp')

    action_filter = request.GET.get('action', '').strip()
    if action_filter:
        logs = logs.filter(action__icontains=action_filter)

    query = request.GET.get('q', '').strip()
    if query:
        logs = logs.filter(
            Q(action__icontains=query) |
            Q(details__icontains=query) |
            Q(target_model__icontains=query) |
            Q(actor__email__icontains=query)
        )

    paginator = Paginator(logs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'dashboard/admin_audit_logs.html', {
        'page_obj': page_obj,
        'search_query': query,
        'action_filter': action_filter
    })

from django.shortcuts import render
from django.views.generic import ListView
from django.utils import timezone
from django.contrib.auth import get_user_model
User = get_user_model()

class UpcomingRenewalMemberListView(ListView):
    model = User
    template_name = 'advadmin/upcoming_renewals.html'
    context_object_name = 'users'
    paginate_by = 15  # Optional

    def get_queryset(self):
        today = timezone.localdate()
        first_day = today.replace(day=1)
        if today.month == 12:
            last_day = today.replace(year=today.year+1, month=1, day=1) - timezone.timedelta(days=1)
        else:
            last_day = today.replace(month=today.month+1, day=1) - timezone.timedelta(days=1)


        print("first_day", first_day)
        print("last_day", last_day)

        return User.objects.filter(
            staff_role='Member',
            is_active=True,
            on_subscription=True,
            package_expiry_date__gte=first_day,
            package_expiry_date__lte=last_day,
        ).order_by('package_expiry_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_name'] = "renewals"
        return context
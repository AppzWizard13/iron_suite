from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now
from .models import Enquiry

def enquiry_list(request):
    date_filter = request.GET.get('date_filter', now().date())  # Default to today's date
    enquiries = Enquiry.objects.filter(date_created__date=date_filter).order_by('-date_created')
    
    return render(request, 'admin_panel/enquiry_list.html', {'enquiries': enquiries, 'date_filter': date_filter})

def toggle_enquiry_status(request, enquiry_id):
    enquiry = get_object_or_404(Enquiry, id=enquiry_id)
    enquiry.status = 'unread' if enquiry.status == 'read' else 'read'
    enquiry.save()
    return redirect('enquiry_list')

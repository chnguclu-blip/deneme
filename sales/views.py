from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SalesOffer, SalesOfferItem, Customer
from .models import SalesOffer, SalesOfferItem, Customer
from .forms import SalesOfferForm, SalesOfferItemFormSet, SalesOfferItemForm, CustomerForm
from django.utils import timezone

@login_required
def sales_list(request):
    offers = SalesOffer.objects.all()
    return render(request, 'sales/offer_list.html', {'offers': offers})

# ... existing offer views ...

# --- Customer Views ---

@login_required
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'sales/customer_list.html', {'customers': customers})

@login_required
def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Müşteri başarıyla eklendi.")
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'sales/customer_form.html', {'form': form, 'title': 'Yeni Müşteri Ekle'})

@login_required
def edit_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, "Müşteri bilgileri güncellendi.")
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'sales/customer_form.html', {'form': form, 'title': 'Müşteri Düzenle'})

@login_required
def delete_customer(request, pk):
    if request.method == 'POST':
        customer = get_object_or_404(Customer, pk=pk)
        customer.delete()
        messages.success(request, "Müşteri silindi.")
    return redirect('customer_list')

@login_required
def create_offer(request):
    if request.method == 'POST':
        form = SalesOfferForm(request.POST)
        formset = SalesOfferItemFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            offer = form.save(commit=False)
            offer.created_by = request.user
            offer.save()
            
            items = formset.save(commit=False)
            for item in items:
                item.offer = offer
                item.save()
            formset.save_m2m() 
            
            messages.success(request, "Satış teklifi başarıyla oluşturuldu.")
            return redirect('sales_list')
    else:
        # Pre-fill with last offer settings if available
        last_offer = SalesOffer.objects.first()
        initial_data = {}
        
        if last_offer:
            initial_data = {
                'company_name': last_offer.company_name,
                'company_address': last_offer.company_address,
                'company_tax_office': last_offer.company_tax_office,
                'company_tax_number': last_offer.company_tax_number,
                'delivery_place': last_offer.delivery_place,
                'advance_payment': last_offer.advance_payment,
                'payment_method': last_offer.payment_method,
                'terms': last_offer.terms,
                'notes': last_offer.notes,
                'bank_recipient': last_offer.bank_recipient,
                'bank_name': last_offer.bank_name,
                'bank_branch': last_offer.bank_branch,
                'bank_iban': last_offer.bank_iban,
                'bank_swift': last_offer.bank_swift,
                'currency': last_offer.currency,
                'language': last_offer.language,
            }
            
        form = SalesOfferForm(initial=initial_data)
        formset = SalesOfferItemFormSet()

    return render(request, 'sales/offer_form.html', {'form': form, 'formset': formset})

@login_required
def edit_offer(request, pk):
    offer = get_object_or_404(SalesOffer, pk=pk)
    
    if request.method == 'POST':
        form = SalesOfferForm(request.POST, instance=offer)
        formset = SalesOfferItemFormSet(request.POST, instance=offer)
        
        if form.is_valid() and formset.is_valid():
            offer = form.save(commit=False)
            # If rejected/approved, maybe reset to waiting or draft?
            # For now, let's reset to WAITING if it was REJECTED, or keep as is.
            # User revised it, so it probably needs re-approval.
            if offer.status in ['REJECTED', 'APPROVED']:
                 offer.status = 'WAITING'
                 offer.approved_by = None
                 offer.approved_at = None
            
            offer.save()
            
            formset.save()
            
            messages.success(request, "Teklif başarıyla güncellendi.")
            return redirect('offer_detail', pk=offer.pk)
    else:
        form = SalesOfferForm(instance=offer)
        # extra=0 prevent phantom empty row on edit
        SalesOfferItemFormSetNoExtra = forms.inlineformset_factory(
            SalesOffer, SalesOfferItem, form=SalesOfferItemForm,
            extra=0, can_delete=True
        )
        formset = SalesOfferItemFormSetNoExtra(instance=offer)
        
    return render(request, 'sales/offer_form.html', {
        'form': form, 
        'formset': formset,
        'title': f"Teklifi Düzenle: {offer.offer_number}"
    })

@login_required
def offer_detail(request, pk):
    offer = get_object_or_404(SalesOffer, pk=pk)
    return render(request, 'sales/offer_detail.html', {'offer': offer})

@login_required
def approve_offer(request, pk):
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "Bu işlem için yetkiniz yok.")
        return redirect('offer_detail', pk=pk)
        
    if request.method == 'POST':
        offer = get_object_or_404(SalesOffer, pk=pk)
        offer.status = 'APPROVED'
        offer.approved_by = request.user
        offer.approved_at = timezone.now()
        offer.save()
        messages.success(request, "Teklif onaylandı.")
        
    return redirect('offer_detail', pk=pk)

@login_required
def reject_offer(request, pk):
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "Bu işlem için yetkiniz yok.")
        return redirect('offer_detail', pk=pk)

    if request.method == 'POST':
        offer = get_object_or_404(SalesOffer, pk=pk)
        offer.status = 'REJECTED'
        offer.save()
        messages.warning(request, "Teklif reddedildi.")
        
    return redirect('offer_detail', pk=pk)

@login_required
def offer_letter(request, pk):
    offer = get_object_or_404(SalesOffer, pk=pk)
    return render(request, 'sales/offer_letter.html', {'offer': offer})
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import os

# ... existing code ...

from django.conf import settings
from django.contrib.staticfiles import finders
import os

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    result = finders.find(uri)
    if result:
        if isinstance(result, (list, tuple)):
            result = result[0]
        return result
        
    sUrl = settings.STATIC_URL        # Typically /static/
    mUrl = settings.MEDIA_URL         # Typically /media/
    mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

    # Convert to standard path
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        # Look in STATICFILES_DIRS first for dev
        uri_path = uri.replace(sUrl, "")
        # Strip leading slashes to prevent os.path.join from treating it as root
        if uri_path.startswith('/'):
            uri_path = uri_path[1:]
        if uri_path.startswith('\\'):
            uri_path = uri_path[1:]
            
        for static_dir in settings.STATICFILES_DIRS:
            path = os.path.join(static_dir, uri_path)
            if os.path.isfile(path):
                return path
        # Then check STATIC_ROOT
        if settings.STATIC_ROOT:
             path = os.path.join(settings.STATIC_ROOT, uri_path)
    else:
        # Absolute path?
        return uri

    # make sure that file exists
    if path and not os.path.isfile(path):
            # raise Exception(
            #     'media URI must start with %s or %s' % (sUrl, mUrl)
            # )
            return None # Fail silently/gracefully if file not found
    return path

@login_required
def generate_offer_pdf(request, pk):
    offer = get_object_or_404(SalesOffer, pk=pk)
    
    
    # PDF Layout CSS (Moved here to avoid IDE linter errors in HTML)
    # Using <style> tags here to trick HTML linter
    pdf_style_block = """
    <style>
        @page {
            size: A4;
            margin: 2cm;
            @frame footer {
                -pdf-frame-content: footerContent;
                bottom: 1cm;
                margin-left: 2cm;
                margin-right: 2cm;
                height: 3cm;
            }
        }
    </style>
    """
    
    template_path = 'sales/offer_pdf.html'
    context = {'offer': offer, 'pdf_style_block': pdf_style_block}
    
    # Create a file-like buffer to receive PDF data
    from io import BytesIO
    buffer = BytesIO()
    
    template = get_template(template_path)
    html = template.render(context)
    
    # Create PDF
    pisa_status = pisa.CreatePDF(
       html, dest=buffer,
       link_callback=link_callback
    )
    
    if pisa_status.err:
         return HttpResponse('We had some errors <pre>' + html + '</pre>')
         
    buffer.seek(0)
    
    # Save PDF to model
    filename = f"teklif_{offer.offer_number}.pdf"
    
    # Delete old file if exists
    if offer.pdf_file:
         try:
             os.remove(offer.pdf_file.path)
         except:
             pass
             
    from django.core.files.base import ContentFile
    offer.pdf_file.save(filename, ContentFile(buffer.read()))
    offer.save()
    
    messages.success(request, f"PDF başarıyla oluşturuldu: {filename}")
    return redirect('offer_detail', pk=pk)

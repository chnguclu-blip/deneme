from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SalesOffer, SalesOfferItem, Customer, OfferProgress
from .forms import SalesOfferForm, SalesOfferItemFormSet, SalesOfferItemForm, CustomerForm
from django.utils import timezone
from django.template.loader import get_template
from xhtml2pdf import pisa
import os
from django.conf import settings

# ... existing code ...

def fetch_resources(uri, rel):
    """
    Callback to allow xhtml2pdf to load local static and media files.
    """
    import os
    if uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.BASE_DIR, uri.replace(settings.STATIC_URL, 'static/'))
        if os.path.isfile(path):
            return os.path.normpath(path)
    elif uri.startswith(settings.MEDIA_URL):
        # Decode the URL to handle any URL-encoded characters like %20 for spaces
        from urllib.parse import unquote
        uri = unquote(uri)
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ''))
        if os.path.isfile(path):
            return os.path.normpath(path)
    # Return empty string if not found to prevent xhtml2pdf crashes
    return ""

@login_required
def send_offer(request, pk):
    offer = get_object_or_404(SalesOffer, pk=pk)
    if offer.status != 'APPROVED':
        messages.error(request, "Yalnızca onaylanmış teklifler gönderilebilir.")
        return redirect('offer_detail', pk=pk)
        
    if request.method == 'POST':
        offer.is_sent = True
        offer.sent_at = timezone.now()
        
        # Determine Folder Name
        folder_name = offer.project_name if offer.project_name else offer.customer.name if offer.customer else "Bilinmeyen Proje"
        # Sanitize folder name
        folder_name = "".join([c for c in folder_name if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        
        # Collect and separate images vs pdfs
        import io
        import pypdf
        images_to_append = []
        pdfs_to_append = []

        for item in offer.items.all():
            doc = None
            title = ""
            if item.product and getattr(item.product, 'attachment', None):
                doc = item.product.attachment
                title = item.product.material_name
            elif item.subpart and getattr(item.subpart, 'visual_doc', None):
                doc = item.subpart.visual_doc
                title = item.subpart.material_name

            if doc and hasattr(doc, 'name'):
                try:
                    ext = os.path.splitext(doc.name)[1].lower()
                    if ext == '.pdf':
                        pdfs_to_append.append({'path': doc.path, 'title': title})
                    elif ext in ['.jpg', '.jpeg', '.png', '.gif']:
                        # xhtml2pdf works best with absolute local file paths for images when `fetch_resources` is spotty.
                        images_to_append.append({'url': doc.path, 'title': title})
                except Exception:
                    pass
        
        # Setup PDF Generation
        template_path = 'sales/offer_letter.html'
        context = {
            'offer': offer,
            'request': request,
            'images_to_append': images_to_append,
            'is_pdf': True,
            'BASE_DIR_PATH': str(settings.BASE_DIR).replace('\\', '/')
        }
        
        response = get_template(template_path)
        html = response.render(context)
        
        # Register Turkish TTF Fonts for reportlab
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        try:
            pdfmetrics.registerFont(TTFont('Roboto', os.path.join(settings.BASE_DIR, 'static/fonts/Roboto-Regular.ttf')))
            pdfmetrics.registerFont(TTFont('Roboto-Bold', os.path.join(settings.BASE_DIR, 'static/fonts/Roboto-Bold.ttf')))
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning("Failed to register Roboto font: %s", e)
        
        # Set Save Directory
        save_dir = os.path.join(settings.MEDIA_ROOT, 'gonderilen_teklifler', folder_name)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        file_name = f"{offer.offer_number}.pdf"
        file_path = os.path.join(save_dir, file_name)
        
        pdf_buffer = io.BytesIO()
        pisa_status = pisa.CreatePDF(html, dest=pdf_buffer, link_callback=fetch_resources)
            
        if pisa_status.err:
            messages.error(request, "Teklif gönderildi olarak işaretlendi ancak PDF oluşturulurken hata oluştu.")
        else:
            pdf_buffer.seek(0)
            if not pdfs_to_append:
                # Direct save if no pdfs to merge
                with open(file_path, "wb") as f:
                    f.write(pdf_buffer.read())
            else:
                try:
                    merger = pypdf.PdfWriter()
                    merger.append(pdf_buffer)
                    for pdf_info in pdfs_to_append:
                        if os.path.exists(pdf_info['path']):
                            merger.append(pdf_info['path'])
                    with open(file_path, "wb") as f:
                        merger.write(f)
                except Exception as e:
                    import traceback
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error("PyPDF Merge Error: %s", str(e))
                    logger.error(traceback.format_exc())
                    # Fallback to non-merged
                    pdf_buffer.seek(0)
                    with open(file_path, "wb") as f:
                        f.write(pdf_buffer.read())

            offer.pdf_file = f'gonderilen_teklifler/{folder_name}/{file_name}'
            messages.success(request, f"Teklif başarıyla gönderildi olarak işaretlendi. PDF kopyası '{folder_name}' klasörüne kaydedildi.")
            
        offer.save()
        
    return redirect('offer_detail', pk=pk)

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
        # Pre-fill with last updated offer settings if available
        last_offer = SalesOffer.objects.order_by('-updated_at').first()
        initial_data = {}
        
        if last_offer:
            initial_data = {
                'company_name': last_offer.company_name,
                'company_address': last_offer.company_address,
                'company_tax_office': last_offer.company_tax_office,
                'company_tax_number': last_offer.company_tax_number,
                # Keep offer_date default to today, but carry over valid dates
                'validity_date': last_offer.validity_date,
                'delivery_date': last_offer.delivery_date,
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
def sent_offers_list(request):
    offers = SalesOffer.objects.filter(is_sent=True)
    return render(request, 'sales/sent_offers_list.html', {
        'offers': offers, 
        'now': timezone.now(),
        'title': 'Gönderilen Teklifler'
    })

@login_required
def offer_letter(request, pk):
    offer = get_object_or_404(SalesOffer, pk=pk)
    return render(request, 'sales/offer_letter.html', {'offer': offer})

@login_required
def offer_progress_detail(request, pk):
    offer = get_object_or_404(SalesOffer, pk=pk)
    if not offer.is_sent:
        messages.warning(request, "Bu teklif henüz gönderilmediği için ilerleme durumu görüntülenemez.")
        return redirect('offer_detail', pk=pk)
    
    progress_updates = offer.progress_updates.all()
    return render(request, 'sales/offer_progress.html', {
        'offer': offer,
        'progress_updates': progress_updates,
        'now': timezone.now(),
        'title': f'Teklif İlerleme Durumu: {offer.offer_number}'
    })

@login_required
def add_offer_progress(request, pk):
    offer = get_object_or_404(SalesOffer, pk=pk)
    if not offer.is_sent:
        return redirect('offer_detail', pk=pk)
        
    if request.method == 'POST':
        status_note = request.POST.get('status_note')
        if status_note:
            OfferProgress.objects.create(
                offer=offer,
                status_note=status_note,
                created_by=request.user
            )
            messages.success(request, "İlerleme durumu eklendi.")
    
    return redirect('offer_progress_detail', pk=pk)

@login_required
def set_offer_alarm(request, pk):
    offer = get_object_or_404(SalesOffer, pk=pk)
    
    if request.method == 'POST':
        try:
            amount = int(request.POST.get('amount', 0))
        except ValueError:
            amount = 0
            
        unit = request.POST.get('unit', 'days')
        
        if amount > 0:
            if unit == 'hours':
                delta = timezone.timedelta(hours=amount)
                unit_display = "saat"
            elif unit == 'months':
                # Approximate month as 30 days
                delta = timezone.timedelta(days=amount * 30)
                unit_display = "ay"
            else: # days
                delta = timezone.timedelta(days=amount)
                unit_display = "gün"
                
            offer.alarm_date = timezone.now() + delta
            offer.save()
            messages.success(request, f"Alarm {amount} {unit_display} sonrasına başarıyla kuruldu.")
        else:
            messages.error(request, "Lütfen geçerli bir süre girin.")
            
    return redirect('offer_progress_detail', pk=pk)


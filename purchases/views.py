from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Supplier, PurchaseProcess, PurchaseRequest
from .forms import SupplierForm, PurchaseProcessForm, PurchaseRequestForm

# --- Supplier Views ---
@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all().order_by('-created_at')
    return render(request, 'purchases/supplier_list.html', {'suppliers': suppliers})

@login_required
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tedarikçi başarıyla eklendi.')
            return redirect('purchases:supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'purchases/supplier_form.html', {'form': form, 'title': 'Yeni Tedarikçi Ekle'})

@login_required
def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, f'{supplier.name} başarıyla güncellendi.')
            return redirect('purchases:supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'purchases/supplier_form.html', {'form': form, 'title': 'Tedarikçi Düzenle'})

@login_required
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        name = supplier.name
        supplier.delete()
        messages.success(request, f'{name} başarıyla silindi.')
        return redirect('purchases:supplier_list')
    return render(request, 'purchases/confirm_delete.html', {'object': supplier, 'type': 'Tedarikçi'})

# --- Purchase Process Views ---
@login_required
def process_list(request):
    processes = PurchaseProcess.objects.all().order_by('-created_at')
    return render(request, 'purchases/process_list.html', {'processes': processes})

@login_required
def process_create(request):
    if request.method == 'POST':
        form = PurchaseProcessForm(request.POST)
        if form.is_valid():
            process = form.save(commit=False)
            process.created_by = request.user
            process.save()
            messages.success(request, 'Süreç başarıyla oluşturuldu.')
            return redirect('purchases:process_list')
    else:
        form = PurchaseProcessForm()
    return render(request, 'purchases/process_form.html', {'form': form, 'title': 'Yeni Süreç Ekle'})

@login_required
def process_edit(request, pk):
    process = get_object_or_404(PurchaseProcess, pk=pk)
    if request.method == 'POST':
        form = PurchaseProcessForm(request.POST, instance=process)
        if form.is_valid():
            form.save()
            messages.success(request, f'{process.title} başarıyla güncellendi.')
            return redirect('purchases:process_list')
    else:
        form = PurchaseProcessForm(instance=process)
    return render(request, 'purchases/process_form.html', {'form': form, 'title': 'Süreç Düzenle'})

@login_required
def process_delete(request, pk):
    process = get_object_or_404(PurchaseProcess, pk=pk)
    if request.method == 'POST':
        title = process.title
        process.delete()
        messages.success(request, f'{title} başarıyla silindi.')
        return redirect('purchases:process_list')
    return render(request, 'purchases/confirm_delete.html', {'object': process, 'type': 'Satın Alma Süreci'})

# --- Purchase Request Views ---
@login_required
def request_list(request):
    requests = PurchaseRequest.objects.all().order_by('-created_at')
    return render(request, 'purchases/request_list.html', {'requests': requests})

@login_required
def request_create(request):
    if request.method == 'POST':
        form = PurchaseRequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.requested_by = request.user
            req.save()
            messages.success(request, 'Satın alma talebi başarıyla oluşturuldu.')
            return redirect('purchases:request_list')
    else:
        form = PurchaseRequestForm()
    return render(request, 'purchases/request_form.html', {'form': form, 'title': 'Yeni Satın Alma Talebi'})

@login_required
def request_edit(request, pk):
    req = get_object_or_404(PurchaseRequest, pk=pk)
    if request.method == 'POST':
        form = PurchaseRequestForm(request.POST, instance=req)
        if form.is_valid():
            form.save()
            messages.success(request, f'{req.product_name} talebi başarıyla güncellendi.')
            return redirect('purchases:request_list')
    else:
        form = PurchaseRequestForm(instance=req)
    return render(request, 'purchases/request_form.html', {'form': form, 'title': 'Talep Düzenle'})

@login_required
def request_delete(request, pk):
    req = get_object_or_404(PurchaseRequest, pk=pk)
    if request.method == 'POST':
        name = req.product_name
        req.delete()
        messages.success(request, f'{name} talebi başarıyla silindi.')
        return redirect('purchases:request_list')
    return render(request, 'purchases/confirm_delete.html', {'object': req, 'type': 'Satın Alma Talebi'})

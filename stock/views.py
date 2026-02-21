from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Max, Q, F, Value, DecimalField
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.core.files import File
from decimal import Decimal, InvalidOperation
import os
import json
import qrcode
from io import BytesIO
from .models import StockItem, StockMovement

def stok_ekle(request):
    if request.method == 'POST':
        product_code = request.POST.get('product_code', '').strip()
        product_name = request.POST.get('product_name', '').strip()
        quality = request.POST.get('quality', '').strip()
        waybill_no = request.POST.get('waybill_no', '').strip()
        description = request.POST.get('description', '').strip()
        stock_area = request.POST.get('stock_area', '').strip()
        unit = request.POST.get('unit', '').strip()
        quantity_input = request.POST.get('quantity')
        document = request.FILES.get('document')
        category = request.POST.get('category', 'HAM MADDE')
        sub_category = request.POST.get('sub_category', '').strip()
        
        # New Fields
        unit_weight_input = request.POST.get('unit_weight')
        shelf_basket = request.POST.get('shelf_basket', '').strip()
        supplier = request.POST.get('supplier', '').strip()
        lot_no = request.POST.get('lot_no', '').strip()
        min_stock_level = request.POST.get('min_stock_level', 0)
        if not min_stock_level:
            min_stock_level = 0

        stock_id = request.POST.get('stock_id')

        quantity = 0
        if quantity_input:
            try:
                quantity = Decimal(quantity_input.replace(',', '.'))
            except InvalidOperation:
                quantity = 0
                
        unit_weight = None
        if unit_weight_input:
            try:
                unit_weight = Decimal(unit_weight_input.replace(',', '.'))
            except InvalidOperation:
                unit_weight = None

        if product_name: # Product Code can be empty now (auto-generated)
            if stock_id:
                item = get_object_or_404(StockItem, id=stock_id)
                if product_code: # Only update if provided, otherwise keep existing
                     item.product_code = product_code
                item.product_name = product_name
                item.quality = quality
                item.waybill_no = waybill_no
                item.description = description
                item.stock_area = stock_area
                item.unit = unit
                item.quantity = quantity
                item.category = category
                item.sub_category = sub_category
                
                # Update new fields
                item.unit_weight = unit_weight
                item.shelf_basket = shelf_basket
                item.supplier = supplier
                item.lot_no = lot_no
                
                if document:
                    item.document = document
                item.save()
                
                # Update QR Code
                # User Request: "mevcut qr kodlar değişmesin" (Don't change existing)
                # "bundan sonra eklenen ürünlerin QR kodu oluşturulurken... veriler oluşturulsun"
                if not item.qr_code and item.product_code:
                     # Generate QR Data (Text based on user request)
                    qr_data = f"Ürün Kodu: {item.product_code}\nLot No: {item.lot_no or '-'}\nStok Alanı: {item.stock_area or '-'}\nRaf No: {item.shelf_basket or '-'}"
                    
                    # Create QR
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(qr_data)
                    qr.make(fit=True)
                    
                    img = qr.make_image(fill_color="black", back_color="white")
                    buffer = BytesIO()
                    img.save(buffer, format="PNG")
                    
                    filename = f"qr_{item.product_code}.png"
                    item.qr_code.save(filename, File(buffer), save=True)

            else:
                item = StockItem.objects.create(
                    product_code=product_code,
                    product_name=product_name,
                    quality=quality,
                    waybill_no=waybill_no,
                    description=description,
                    stock_area=stock_area,
                    unit=unit,
                    quantity=quantity,
                    initial_quantity=quantity, # Set initial quantity
                    document=document,
                    category=category,
                    sub_category=sub_category,
                    unit_weight=unit_weight,
                    shelf_basket=shelf_basket,
                    supplier=supplier,
                    lot_no=lot_no,
                    min_stock_level=min_stock_level,
                    created_by=request.user if request.user.is_authenticated else None
                )
                
                # Generate QR Code for New Item
                if item.product_code:
                     # Generate QR Data (Text based on user request)
                    qr_data = f"Ürün Kodu: {item.product_code}\nLot No: {item.lot_no or '-'}\nStok Alanı: {item.stock_area or '-'}\nRaf No: {item.shelf_basket or '-'}"
                    
                    # Create QR
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(qr_data)
                    qr.make(fit=True)
                    
                    img = qr.make_image(fill_color="black", back_color="white")
                    buffer = BytesIO()
                    img.save(buffer, format="PNG")
                    
                    filename = f"qr_{item.product_code}.png"
                    item.qr_code.save(filename, File(buffer), save=True)
            return redirect('stok_ekle')

    stock_items = StockItem.objects.all().order_by('-created_at')
    
    # Calculate counts/data for cards
    counts = {
        'HAM MADDE': stock_items.filter(category='HAM MADDE').count(),
        'YARI MAMUL': stock_items.filter(category='YARI MAMUL').count(),
        'MAMUL': stock_items.filter(category='MAMUL').count(),
        'SARF MALZEME': stock_items.filter(category='SARF MALZEME').count(),
        'HIRDAVAT': stock_items.filter(category='HIRDAVAT').count(),
    }

    # Sub-category counts for HAM MADDE
    # We want to ensure these specific sub-categories are always present in the context, even if count is 0
    ham_madde_subs = ['BORU', 'PROFİL', 'SAC', 'DOLU', 'TEL', 'KÜLÇE']
    sub_counts = {}
    
    # Get actual counts from DB
    db_counts = stock_items.filter(category='HAM MADDE').values('sub_category').annotate(count=Count('id'))
    db_count_map = {item['sub_category']: item['count'] for item in db_counts}
    
    for sub in ham_madde_subs:
        # Replace spaces with underscores for template accessibility (e.g., "DOLU MALZEME" -> "DOLU_MALZEME")
        safe_key = sub.replace(' ', '_')
        # Check for both the underscored version and the spaced version (legacy data)
        count = db_count_map.get(sub, 0)
        if sub == 'DOLU':
             count += db_count_map.get('DOLU MALZEME', 0)
             count += db_count_map.get('DOLU_MALZEME', 0)
        
        sub_counts[safe_key] = count
    
    return render(request, 'stock/stok_ekle.html', {'stock_items': stock_items, 'counts': counts, 'sub_counts': sub_counts})

def delete_stock(request, pk):
    if request.method == 'POST':
        item = get_object_or_404(StockItem, pk=pk)
        item.delete()
    return redirect('stok_ekle')



def stock_detail(request, pk):
    stock = get_object_or_404(StockItem, pk=pk)
    return render(request, 'stock/stock_detail.html', {'stock': stock})

def stok_home(request):
    return render(request, 'stock/stok_home.html')

@login_required
def stok_goruntule(request):
    # Get all entries aggregated by product name
    entries = StockItem.objects.values('product_name', 'unit').annotate(
        total_initial=Sum('initial_quantity'),
        last_updated=Max('created_at')
    )
    
    # Get all exits aggregated by product name
    exits = StockMovement.objects.filter(movement_type='OUT').values('stock_item__product_name').annotate(
        total_out=Sum('quantity')
    )
    
    # Create a dictionary for exits for O(1) lookup
    exit_map = {item['stock_item__product_name']: item['total_out'] for item in exits}
    
    aggregated_stock = []
    for entry in entries:
        name = entry['product_name']
        total_in = entry['total_initial'] or 0
        total_out = exit_map.get(name, 0)
        net_quantity = total_in - total_out
        
        aggregated_stock.append({
            'product_name': name,
            'unit': entry['unit'],
            'total_quantity': net_quantity,
            'last_updated': entry['last_updated']
        })
        
    # Sort carefully (converting list back to something renderable, list is fine)
    aggregated_stock.sort(key=lambda x: x['product_name'])
    
    return render(request, 'stock/stok_goruntule.html', {'aggregated_stock': aggregated_stock})

@login_required
def stok_detay_list(request, product_name):
    # Filter by product name to show all individual entries (batches)
    # Order by creation date descending
    items = StockItem.objects.filter(product_name=product_name).order_by('-created_at')
    
    # Calculate Per-Item Stats
    # total_exit_annotated: Sum of 'OUT' movements for each specific item
    # net_stock_annotated: initial_quantity - total_exit_annotated
    items = items.annotate(
        total_exit_annotated=Coalesce(
            Sum('movements__quantity', filter=Q(movements__movement_type='OUT')),
            Value(0),
            output_field=DecimalField()
        )
    ).annotate(
        net_stock_annotated=F('initial_quantity') - F('total_exit_annotated')
    )

    # Calculate Global Summaries (for the top info cards)
    total_entry_global = items.aggregate(Sum('initial_quantity'))['initial_quantity__sum'] or 0
    
    # For global exit, we can sum the annotated exits or query directly
    # Querying directly is safer to catch any consistency issues, but summing annotated should be same.
    # Let's simple query for global stats to match previous logic perfectly.
    global_exits = StockMovement.objects.filter(stock_item__product_name=product_name, movement_type='OUT')
    total_exit_global = global_exits.aggregate(Sum('quantity'))['quantity__sum'] or 0
    net_stock_global = total_entry_global - total_exit_global
    
    # Get Critical Stock Level (From the most recent item, or default 10)
    last_item = items.first() # items is ordered by -created_at
    min_stock = last_item.min_stock_level if last_item else 10
    unit = last_item.unit if last_item else ''
    
    # Determine Status Color (Global Status)
    threshold_green = min_stock * Decimal('1.50')
    threshold_yellow = min_stock * Decimal('1.10')
    
    if net_stock_global > threshold_green:
        status_color = 'bg-green-100 text-green-800 border-green-200'
        icon_color = 'text-green-500'
        status_text = 'Stok Durumu İyi'
    elif net_stock_global > min_stock:
        status_color = 'bg-yellow-100 text-yellow-800 border-yellow-200'
        icon_color = 'text-yellow-500'
        status_text = 'Stok Kritik Seviyeye Yakın'
    else:
        status_color = 'bg-red-100 text-red-800 border-red-200'
        icon_color = 'text-red-500'
        status_text = 'Kritik Stok Seviyesi!'

    context = {
        'items': items, 
        'product_name': product_name,
        # 'exits': exits, # Removed as we are not listing raw exits anymore
        'summary': {
            'total_entry': total_entry_global,
            'total_exit': total_exit_global,
            'net_stock': net_stock_global,
            'min_stock': min_stock,
            'unit': unit,
            'status_color': status_color,
            'icon_color': icon_color,
            'status_text': status_text
        }
    }
    return render(request, 'stock/stok_detay_list.html', context)

@login_required
def check_stock_code(request):
    code = request.GET.get('code', '').strip()
    if not code:
        return JsonResponse({'valid': False})
    
    try:
        stock = StockItem.objects.get(product_code=code)
        
        # Calculate Global Net Stock for this product
        total_entry = StockItem.objects.filter(product_name=stock.product_name).aggregate(Sum('initial_quantity'))['initial_quantity__sum'] or 0
        total_exit = StockMovement.objects.filter(stock_item__product_name=stock.product_name, movement_type='OUT').aggregate(Sum('quantity'))['quantity__sum'] or 0
        net_stock = total_entry - total_exit
        
        return JsonResponse({
            'valid': True, 
            'pk': stock.pk,
            'product_code': stock.product_code,
            'product_name': stock.product_name,
            'quantity': stock.quantity, 
            'net_stock': net_stock, 
            'unit': stock.unit,
            'category': stock.category,
            'sub_category': stock.sub_category,
            'stock_area': stock.stock_area,
            'shelf_basket': stock.shelf_basket,
            'quality': stock.quality,
            'unit_weight': stock.unit_weight,
            'waybill_no': stock.waybill_no,
            'supplier': stock.supplier,
            'lot_no': stock.lot_no,
            'description': stock.description,
            'created_at': stock.created_at.strftime('%d.%m.%Y %H:%M'),
            'created_by': stock.created_by.username if stock.created_by else '',
            'document_url': stock.document.url if stock.document else '',
            'is_image': stock.document.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')) if stock.document else False,
            'qr_code_url': stock.qr_code.url if stock.qr_code else ''
        })

    except StockItem.DoesNotExist:
        return JsonResponse({'valid': False})

@login_required
def stok_cikis(request):
    if request.method == 'POST':
        product_code = request.POST.get('product_code')
        quantity = float(request.POST.get('quantity', 0))
        project = request.POST.get('project')
        receiver = request.POST.get('receiver')
        
        try:
            stock = StockItem.objects.get(product_code=product_code)
            
            # Create StockMovement record
            StockMovement.objects.create(
                stock_item=stock,
                quantity=quantity,
                movement_type='OUT',
                project=project,
                receiver=receiver,
                performer=request.user
            )
            messages.success(request, f"{quantity} {stock.unit} '{stock.product_name}' başarıyla çıkıldı (Stok düşülmedi).")

        except StockItem.DoesNotExist:
            messages.error(request, "Ürün bulunamadı!")
            
        return redirect('stok_cikis')

    # Get recent movements
    recent_movements = StockMovement.objects.filter(movement_type='OUT').order_by('-created_at')[:20]
    return render(request, 'stock/stok_cikis.html', {'recent_movements': recent_movements})

@login_required
def delete_stock_movement(request, pk):
    movement = get_object_or_404(StockMovement, pk=pk)
    
    # Return stock logic removed as per request (stock is not deducted on exit anymore)

    
    movement.delete()
    messages.success(request, "Çıkış kaydı silindi.")
    return redirect('stok_cikis')

@login_required
def edit_stock_movement(request, pk):
    movement = get_object_or_404(StockMovement, pk=pk)
    
    if request.method == 'POST':
        new_quantity = float(request.POST.get('quantity', 0))
        project = request.POST.get('project')
        receiver = request.POST.get('receiver')
        
        # Calculate diff
        # Stock deduction logic removed as per request

        
        movement.quantity = new_quantity
        movement.project = project
        movement.receiver = receiver
        movement.save()
        
        messages.success(request, "Kayıt güncellendi.")
        return redirect('stok_cikis')
        
    return render(request, 'stock/stok_cikis_duzenle.html', {'movement': movement})


@login_required
def update_critical_stock(request):
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        new_val = request.POST.get('min_stock_level')
        
        try:
            val = Decimal(new_val)
            # Update ALL stock items for this product to keep it consistent
            StockItem.objects.filter(product_name=product_name).update(min_stock_level=val)
            messages.success(request, "Kritik stok seviyesi güncellendi.")
        except Exception as e:
            messages.error(request, "Güncelleme hatası!")
            
        # Redirect back to detail page
        # Find a valid slug/pk or just use referer
        return redirect(request.META.get('HTTP_REFERER', 'stok_home'))
    return redirect('stok_home')


@login_required
def get_stock_movements_modal(request, pk):
    stock = get_object_or_404(StockItem, pk=pk)
    # Get all OUT movements for this specific stock item
    exits = StockMovement.objects.filter(stock_item=stock, movement_type='OUT').order_by('-created_at')
    
    return render(request, 'stock/partials/stock_movements_modal.html', {
        'stock': stock,
        'exits': exits
    })

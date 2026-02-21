from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Count, Sum, Max
from django.urls import reverse
from django.core.files import File

from decimal import Decimal, InvalidOperation
import os
import shutil
import json
import qrcode
import logging
from io import BytesIO

logger = logging.getLogger(__name__)

from .models import Product, SubPart, ProductSubPart, SubPartMaterial
from stock.models import StockItem

def _handle_subparts(product, subpart_ids, quantities):
    """Helper to handle subpart association and file copying."""
    # Clear existing to ensure clean state (safe for new products too)
    product.subparts.all().delete()
    
    for s_id, qty in zip(subpart_ids, quantities):
        if s_id and qty:
            ProductSubPart.objects.create(
                product=product,
                subpart_id=s_id,
                quantity=qty
            )
            
            # Copy subpart files to product directory
            try:
                subpart = SubPart.objects.get(id=s_id)
                target_dir = os.path.join(settings.MEDIA_ROOT, 'ürünler', product.material_name.strip(), 'alt parçalar', subpart.material_name.strip())
                
                if subpart.quality_doc or subpart.visual_doc:
                    os.makedirs(target_dir, exist_ok=True)
                    
                    if subpart.quality_doc:
                        src = subpart.quality_doc.path
                        dst = os.path.join(target_dir, os.path.basename(subpart.quality_doc.name))
                        if os.path.exists(src):
                            shutil.copy2(src, dst)
                    
                    if subpart.visual_doc:
                        src = subpart.visual_doc.path
                        dst = os.path.join(target_dir, os.path.basename(subpart.visual_doc.name))
                        if os.path.exists(src):
                            shutil.copy2(src, dst)
            except Exception as e:
                logger.error(f"Error copying subpart file: {e}")


def urun_ekle(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        material_code = request.POST.get('material_code', '').strip()
        material_name = request.POST.get('material_name', '').strip()
        weight_input = request.POST.get('weight')
        standard = request.POST.get('standard', '').strip()
        country = request.POST.get('country', '').strip()
        attachment = request.FILES.get('attachment')

        # Clean weight input (comma -> dot)
        weight = None
        if weight_input:
            try:
                weight = Decimal(weight_input.replace(',', '.'))
            except InvalidOperation:
                weight = None

        if material_code and material_name and weight is not None:
            if product_id:
                product = get_object_or_404(Product, id=product_id)
                product.material_code = material_code
                product.material_name = material_name
                product.weight = weight
                product.standard = standard
                product.country = country
                if attachment:
                    product.attachment = attachment
                product.save()
            else:
                product = Product.objects.create(
                    material_code=material_code,
                    material_name=material_name,
                    weight=weight,
                    standard=standard,
                    country=country,
                    attachment=attachment
                )
            
            # Handle Subparts (Common Logic)
            subpart_ids = request.POST.getlist('subparts[]')
            quantities = request.POST.getlist('quantities[]')
            _handle_subparts(product, subpart_ids, quantities)
                        
            return redirect('urun_ekle')

    products_qs = Product.objects.all().prefetch_related('subparts__subpart').order_by('-id')
    products = []
    for product in products_qs:
        media = []
        if product.attachment:
            media.append({
                "type": "main",
                "title": f"Ürün: {product.material_name}",
                "url": product.attachment.url
            })
            
        for psp in product.subparts.all():
            url = psp.get_visual_doc_url()
            if url:
                media.append({
                    "type": "sub",
                    "title": f"Alt: {psp.subpart.material_name}",
                    "url": url
                })
        
        product.media_json = json.dumps(media)
        
        # Prepare subparts data for edit
        subparts_data = []
        for psp in product.subparts.all():
            subparts_data.append({
                'id': psp.subpart.id,
                'name': f"{psp.subpart.material_code} - {psp.subpart.material_name}",
                'quantity': psp.quantity,
                'url': psp.get_visual_doc_url() or ''
            })
        product.subparts_json = json.dumps(subparts_data)
        
        products.append(product)

    all_subparts = SubPart.objects.all().order_by('material_name')
    return render(request, 'products/urun_ekle.html', {'products': products, 'all_subparts': all_subparts})

def delete_product(request, pk):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=pk)
        product.delete()
    return redirect('urun_ekle')

def alt_parca(request):
    if request.method == 'POST':
        subpart_id = request.POST.get('subpart_id')
        material_code = request.POST.get('material_code', '').strip()
        material_name = request.POST.get('material_name', '').strip()
        weight_input = request.POST.get('weight')
        quality = request.POST.get('quality', '').strip()
        description = request.POST.get('description', '').strip()
        quality_doc = request.FILES.get('quality_doc')
        visual_doc = request.FILES.get('visual_doc')

        # Clean weight
        weight = None
        if weight_input:
            try:
                weight = Decimal(weight_input.replace(',', '.'))
            except InvalidOperation:
                weight = None
        
        if material_code and material_name and weight is not None:
            if subpart_id:
                subpart = get_object_or_404(SubPart, id=subpart_id)
                subpart.material_code = material_code
                subpart.material_name = material_name
                subpart.weight = weight
                subpart.quality = quality
                subpart.description = description
                if quality_doc:
                    subpart.quality_doc = quality_doc
                if visual_doc:
                    subpart.visual_doc = visual_doc
                subpart.save()
            else:
                subpart = SubPart.objects.create(
                    material_code=material_code,
                    material_name=material_name,
                    weight=weight,
                    quality=quality,
                    description=description,
                    quality_doc=quality_doc,
                    visual_doc=visual_doc
                )
            
            # --- Handle SubPart Materials ---
            # 1. Clear existing materials for this subpart (Full Sync Strategy)
            SubPartMaterial.objects.filter(subpart=subpart).delete()
            
            # 2. Get Lists from POST
            # Expected format: material_ids[], material_units[], fireli_weights[], etc.
            m_ids = request.POST.getlist('material_stock_ids[]')
            m_units = request.POST.getlist('material_units[]')
            m_amounts = request.POST.getlist('material_amounts[]')
            m_fireli = request.POST.getlist('material_fireli[]')
            m_net = request.POST.getlist('material_net[]')
            m_galvanized = request.POST.getlist('material_galvanized[]')
            m_total = request.POST.getlist('material_total[]')
            m_prices = request.POST.getlist('material_price[]')
            
            # 3. Iterate and Create
            # We assume all lists are same length. Using zip_longest might be safer but zip is fine if JS ensures integrity
            for i in range(len(m_ids)):
                if m_ids[i]: # Ensure there is a stock item selected
                    try:
                        stock_item = StockItem.objects.get(id=m_ids[i])
                        
                        def parse_decimal(val):
                            if not val: return 0
                            try: return Decimal(val.replace(',', '.'))
                            except: return 0

                        SubPartMaterial.objects.create(
                            subpart=subpart,
                            stock_item=stock_item,
                            unit=m_units[i],
                            amount=parse_decimal(m_amounts[i]),
                            fireli_weight=parse_decimal(m_fireli[i]),
                            net_weight=parse_decimal(m_net[i]),
                            galvanized_weight=parse_decimal(m_galvanized[i]),
                            total_weight=parse_decimal(m_total[i]),
                            unit_price=parse_decimal(m_prices[i])
                        )
                    except StockItem.DoesNotExist:
                        continue


            return redirect('alt_parca')

    subparts = SubPart.objects.all().prefetch_related('materials__stock_item').order_by('-id')
    stock_items = StockItem.objects.all().order_by('product_name')
    
    # Prepare Stock Items JSON for JS
    stock_items_list = []
    for item in stock_items:
        stock_items_list.append({
            'id': item.id,
            'name': f"{item.product_name} ({item.product_code})"
        })
    stock_items_json = json.dumps(stock_items_list)
    
    # Pre-fetch materials for edit mode (populate JS)
    for sp in subparts:
        materials = []
        for mat in sp.materials.all():
            materials.append({
                'stock_id': mat.stock_item.id,
                'stock_name': mat.stock_item.product_name,
                'unit': mat.unit,
                'amount': str(mat.amount),
                'fireli': str(mat.fireli_weight),
                'net': str(mat.net_weight),
                'galvanized': str(mat.galvanized_weight),
                'total': str(mat.total_weight),
                'price': str(mat.unit_price)
            })
        sp.materials_json = json.dumps(materials)

    return render(request, 'products/alt_parca.html', {'subparts': subparts, 'stock_items_json': stock_items_json})

def delete_subpart(request, pk):
    if request.method == 'POST':
        subpart = get_object_or_404(SubPart, pk=pk)
        subpart.delete()
    return redirect('alt_parca')

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'products/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def home(request):
    return render(request, 'products/home.html')

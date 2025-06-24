from .models import Product , Category, Order , ProductPrice
from requests.auth import HTTPBasicAuth
from datetime import timedelta ,datetime
from collections import defaultdict
from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from celery import shared_task
import requests
import datetime
import logging
logger = logging.getLogger('celery_tasks')
@shared_task
def refresh_products_cache():

    url = "http://93.170.11.10:8088/RM_OPT/hs/online/stock/update"
    username = "Online"
    password = "cJXGLytPHb3nDNZf5gRh7jzwa"
    try:
        response = requests.post(url, auth=HTTPBasicAuth(username, password), stream=True, json={},)
        data = response.json().get('array', [])
    except Exception as e:
        logger.error(f"Request failed: {e},")
        return

    uid_list = []
    unique_ids = []

    for item in data:
        try:
            uid_list.append(int(item.get("UID")))
            unique_ids.append(item.get('УникальныйИдентификатор'))
        except (TypeError, ValueError):
            continue


    products = {p.uid: p for p in Product.objects.filter(uid__in=uid_list)}
    existing_prices = {p.unique_identifier: p for p in ProductPrice.objects.filter(unique_identifier__in=unique_ids)}
    categories = {c.name: c for c in Category.objects.all()}


    products_to_update = []
    product_prices_to_create = []
    product_prices_to_update = []
    new_categories = {}

    for item in data:
        try:
            uid = int(item.get("UID"))
            product = products.get(uid)
            if not product:
                continue

            category_name = item.get("Class") or "None-Class"
            if category_name not in categories and category_name not in new_categories:
                new_categories[category_name] = Category(name=category_name)
            
            category = categories.get(category_name) or new_categories.get(category_name)
            
            product.category = category
            product.producer = item.get("Producer", "")
            product.country = item.get("Country", "")
            product.mnn = item.get("MNN", "")
            product.release_form = item.get("ReleaseForm", "")
            
            
            ProductType   = item.get("ProductType", "")
            if ProductType == "Rx":
                ProductType = "Рецепт билан"
            elif ProductType == "ОТС":
                ProductType = "Рецептсиз"
            product.product_type = ProductType
           
           
            product.exp_date = item.get("ExpDate")
            product.ikpu = item.get("IKPU", "")
            product.package_code = item.get("PackageCode", "")
            product.vat_percent = item.get("VATPercent", 12)
            product.inn = item.get("INN", "")
            
            if new_name := item.get("Name"):
                product.name = new_name
            
            products_to_update.append(product)

            
            unique_id = item.get('УникальныйИдентификатор')
            if not unique_id:
                continue
                
            price_val = int(item.get("Price", 0))
            amount_val = int(item.get('Amount', 0))
            amount_val = int(item.get('Amount', 0))
            if amount_val < 0:
                amount_val = 0 
                # logger.warning(f"Skipped item with negative amount: {amount_val}, UID: {item.get('UID')}")
                # continue
            if unique_id in existing_prices:
                price_obj = existing_prices[unique_id]
                price_obj.price = price_val
                price_obj.amount = amount_val
                price_obj.product = product
                product_prices_to_update.append(price_obj)
            else:
                product_prices_to_create.append(
                    ProductPrice(
                        unique_identifier=unique_id,
                        product=product,
                        price=price_val,
                        amount=amount_val
                    )
                )
                
        except Exception as e:
            logger.warning(f"Error processing item {item.get('UID')} : {e},")


    with transaction.atomic():

        if new_categories:
            Category.objects.bulk_create(new_categories.values())
            categories.update({c.name: c for c in Category.objects.filter(name__in=new_categories.keys())},)
        

        if products_to_update:
            Product.objects.bulk_update(
                products_to_update,
                fields=[
                    "category", "producer", "country", "mnn", "release_form",
                    "product_type", "exp_date", "ikpu", "package_code",
                    "vat_percent", "inn", "name"
                ]
            )
        

        if product_prices_to_update:
            ProductPrice.objects.bulk_update(
                product_prices_to_update,
                fields=["price", "amount", "product"]
            )
        
        if product_prices_to_create:
            ProductPrice.objects.bulk_create(product_prices_to_create)

    logger.info(f"Successfully updated {len(products_to_update)}, products and {len(product_prices_to_update) + len(product_prices_to_create)}, prices price={product_prices_to_update}  data={len(data)}")


@shared_task
def delete_unpaid_completed_orders():
    """
    Delete orders that are older than 15 minutes, marked as completed but not paid
    """
    try:
        cutoff_time = timezone.now() - timedelta(minutes=15)

        orders = Order.objects.filter(
            is_completed=True,
            is_paid=False,
            created_at__lt=cutoff_time
        )
        count = orders.count()
        orders.delete()
        logger.info(f"Deleted {count}, completed but unpaid orders older than 15 minutes at {datetime.datetime.now()},")
    except Exception as e:
        logger.error(f"Failed to delete unpaid completed orders: {e},")


@shared_task
def delete_ProductPrice():
    ProductPrice.objects.filter(Q(amount=0) | Q(price=0)).delete()
    for product in Product.objects.all():
        price_map = defaultdict(list)

        for pp in product.product_prise.all():
            price_map[pp.price].append(pp)

        for same_price_list in price_map.values():
            if len(same_price_list) > 1:
            
                same_price_list.sort(key=lambda x: x.id, reverse=True)

                to_delete = same_price_list[1:]
                for item in to_delete:
                    # print(f"Deleting duplicate ProductPrice id={item.id} for product id={product.id}, price={item.price}")
                    item.delete()

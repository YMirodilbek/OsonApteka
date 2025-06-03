from requests.auth import HTTPBasicAuth
from .models import Product , Category, Order
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import requests
import datetime
import logging
import redis
import json

logger = logging.getLogger('celery_tasks')
r = redis.Redis(host='localhost', port=6379, db=0)

@shared_task
def refresh_products_cache():
    url = "http://93.170.11.10:8088/RM_OPT/hs/online/stock"
    username = "Online"
    password = "cJXGLytPHb3nDNZf5gRh7jzwa"

    try:
        response = requests.post(url, auth=HTTPBasicAuth(username, password), stream=True, json={})
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return

    if response.status_code != 200:
        logger.error(f"Failed to refresh product data! Status code: {response.status_code}")
        return

    data = response.json().get('array', [])
    uid_list = []

    for item in data:
        try:
            amount = item.get('Amount')
            if amount <=0 :
                continue
            uid_list.append(int(item.get("UID")))

        except (TypeError, ValueError):
            continue

    products = Product.objects.filter(uid__in=uid_list)
    products_dict = {p.uid: p for p in products}

    final_result_dict = {}  # uid -> product_data
    grouped_by_class = {}

    for item in data:
        amount = item.get('Amount')
        if amount <=0 :
            continue
        # try:
        #     Category.objects.get_or_create(name=item.get('Class'))
        # except:pass
        try:
            uid = int(item.get("UID"))
        except (TypeError, ValueError):
            continue

        product = products_dict.get(uid)
        if not product:
            continue

        name = item.get("Name", "")
        category = item.get("Class", "") or "None-Class"
        price = item.get("Price", 0)
        ikpu = item.get("IKPU", "")
        package_code = item.get("PackageCode", "")
        inn = item.get("INN", "")
        vat_percent = item.get("VATPercent", 12)  # Default 12% if not provided

        # Calculate VAT amount using the formula: VAT = (Price / 1.12) × 0.12
        vat_amount = (price / 1.12) * 0.12 if price > 0 else 0

        # Create fiscal_items dict according to the required structure
        fiscal_items = {
            "Name": name,
            "SPIC": ikpu,
            "PackageCode": package_code,
            "Price": price * 100,
            # "Amount": amount, TODO: # amount should be get from order item product quantity # noqa
            "VAT": vat_amount * 100,
            "VATPercent": vat_percent,  # This should now be 12 from API or default
            "CommissionInf": {
                "TIN": inn,
            }
        }

        if uid in final_result_dict:
            if price not in final_result_dict[uid]["prices"]:
                final_result_dict[uid]["prices"].append(price)
            if price not in final_result_dict[uid]["amount"]:
                final_result_dict[uid]["amount"].append(f"{amount} штук  {price} сум ")
                
        else:
            ProductType = item.get("ProductType", "")
            if isinstance(ProductType, list) and ProductType:
                ProductType = ProductType[0]
            else:
                ProductType = ProductType


            if ProductType == "Rx":
                ProductType = "Рецепт билан"
            elif ProductType == "ОТС":
                ProductType = "Рецептсиз"
            if product.name != name:
                product.name = name
                product.save()
            final_result_dict[uid] = {
                "uid": uid,
                "id": product.id,
                "name": name,
                "name_lower": name.lower(),
                "prices": [price],
                "class": category,
                "producer": item.get("Producer", ""),
                "country": item.get("Country", ""),
                "MNN": item.get("MNN", ""),
                "ReleaseForm": item.get("ReleaseForm", ""),
                "ProductType": ProductType,
                "ExpDate": item.get("ExpDate", ""),

                "amount": [f"{amount} штук {price} сум "],
                "image1": product.image1.url if product.image1 else "",
                "fiscal_items": fiscal_items,
            }

    final_result = list(final_result_dict.values())

    for item in final_result:
        category = item["class"]
        grouped_by_class.setdefault(category, []).append(item)

    r.setex('final_result', 86400, json.dumps(final_result))
    r.setex('products_by_class', 86400, json.dumps(grouped_by_class))

    logger.info(f"Redis cache updated successfully! {datetime.datetime.now()}")
    


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
        logger.info(f"Deleted {count} completed but unpaid orders older than 15 minutes at {datetime.datetime.now()}")
    except Exception as e:
        logger.error(f"Failed to delete unpaid completed orders: {e}")


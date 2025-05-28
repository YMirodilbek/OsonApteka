from requests.auth import HTTPBasicAuth
from .models import Product , Category
from celery import shared_task
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
            if int(item.get('Amount')) <=0:
                continue
            uid_list.append(int(item.get("UID")))
        except (TypeError, ValueError):
            continue

    products = Product.objects.filter(uid__in=uid_list)
    products_dict = {p.uid: p for p in products}

    final_result_dict = {}  # uid -> product_data
    grouped_by_class = {}

    for item in data:
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
        vat_percent = item.get("VATPercent", 0)

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
            "VATPercent": vat_percent,
            "CommissionInf": {
                "TIN": inn,
            }
        }

        if uid in final_result_dict:
            if price not in final_result_dict[uid]["prices"]:
                final_result_dict[uid]["prices"].append(price)
        else:
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
                "ProductType": item.get("ProductType", ""),
                "ExpDate": item.get("ExpDate", ""),
                "info": product.info,
                "image1": product.image1.url if product.image1 else "",
                "fiscal_items": fiscal_items,
            }

    final_result = list(final_result_dict.values())

    for item in final_result:
        category = item["class"]
        grouped_by_class.setdefault(category, []).append(item)
        # logger.info(f"{item}")

    r.setex('final_result', 86400, json.dumps(final_result))
    r.setex('products_by_class', 86400, json.dumps(grouped_by_class))

    logger.info(f"Redis cache updated successfully! {datetime.datetime.now()}")

# from celery import shared_task
# import requests
# import datetime
# import logging
# import redis
# import json
# from requests.auth import HTTPBasicAuth
# from .models import Product, Category

# logger = logging.getLogger('celery_tasks')
# r = redis.Redis(host='localhost', port=6379, db=0)

# API_URL = "http://93.170.11.10:8088/RM_OPT/hs/online/stock"
# USERNAME = "Online"
# PASSWORD = "cJXGLytPHb3nDNZf5gRh7jzwa"

# @shared_task
# def refresh_products_cache():
#     try:
#         response = requests.post(API_URL, auth=HTTPBasicAuth(USERNAME, PASSWORD), stream=True, json={})
#         response.raise_for_status()
#     except requests.RequestException as e:
#         logger.error(f"Request failed: {e}")
#         return

#     data = response.json().get('array', [])
#     uid_list = [int(item.get("UID")) for item in data if item.get('Amount', 0) > 0]

#     # Batch fetch products
#     products = Product.objects.filter(uid__in=uid_list)
#     products_dict = {p.uid: p for p in products}

#     final_result_dict = {}
#     categories_to_create = set()

#     for item in data:
#         try:
#             uid = int(item.get("UID"))
#             product = products_dict.get(uid)
#             if not product:
#                 continue

#             category_name = item.get("Class", "None-Class")
#             categories_to_create.add(category_name)

#             price = item.get("Price", 0)
#             if uid in final_result_dict:
#                 if price not in final_result_dict[uid]["prices"]:
#                     final_result_dict[uid]["prices"].append(price)
#             else:
#                 final_result_dict[uid] = {
#                     "uid": uid,
#                     "id": product.id,
#                     "name": item.get("Name", ""),
#                     "name_lower": item.get("Name", "").lower(),
#                     "prices": [price],
#                     "class": category_name,
#                     "producer": item.get("Producer", ""),
#                     "country": item.get("Country", ""),
#                     "MNN": item.get("MNN", ""),
#                     "ReleaseForm": item.get("ReleaseForm", ""),
#                     "ProductType": item.get("ProductType", ""),
#                     "ExpDate": item.get("ExpDate", ""),
#                     "info": product.info,
#                     "image1": product.image1.url if product.image1 else "",
#                 }

#         except (TypeError, ValueError):
#             continue

#     # Bulk create categories
#     Category.objects.bulk_create([Category(name=name) for name in categories_to_create], ignore_conflicts=True)

#     final_result = list(final_result_dict.values())
#     grouped_by_class = {}

#     for item in final_result:
#         category = item["class"]
#         grouped_by_class.setdefault(category, []).append(item)

#     # Store results in Redis
#     r.setex('final_result', 86400, json.dumps(final_result))
#     r.setex('products_by_class', 86400, json.dumps(grouped_by_class))

#     logger.info(f"Redis cache updated successfully! {datetime.datetime.now()}")

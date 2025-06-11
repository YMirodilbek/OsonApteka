from .models import Product , Category, Order , ProductPrice
from requests.auth import HTTPBasicAuth
from django.db import transaction
from datetime import timedelta ,datetime
from django.utils import timezone
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

    logger.info(f"Successfully updated {len(products_to_update)}, products and {len(product_prices_to_update) + len(product_prices_to_create)}, prices")

   
   
   
    # uid_list = []
    # data = response.json().get('array', []) 
    # for item in data:
    #     try:
    #         amount = item.get('Amount')
    #         if amount <=0 :
    #             continue
    #         uid_list.append(int(item.get("UID")))

    #     except (TypeError, ValueError):
    #         continue

    # products = Product.objects.filter(uid__in=uid_list)
    # products_dict = {p.uid: p for p in products},

    # final_result_dict = {}, 
    # grouped_by_class = {},

    # for item in data:
    #     amount = item.get('Amount')
    #     if amount <=0 :
    #         continue
    #     try:
    #         Category.objects.get_or_create(name=item.get('Class'))
    #     except:pass
    #     try:
    #         uid = int(item.get("UID"))
    #     except (TypeError, ValueError):
    #         continue

    #     product = products_dict.get(uid)
    #     if not product:
    #         continue

    #     name = item.get("Name", "")
    #     category = item.get("Class", "") or "None-Class"
    #     price = item.get("Price", 0)
    #     ikpu = item.get("IKPU", "")
    #     package_code = item.get("PackageCode", "")
    #     inn = item.get("INN", "")
    #     vat_percent = item.get("VATPercent", 12)  # Default 12% if not provided

    #     # Calculate VAT amount using the formula: VAT = (Price / 1.12) × 0.12
        # vat_amount = (price / 1.12) * 0.12 if price > 0 else 0

        # Create fiscal_items dict according to the required structure
        # fiscal_items = {
        #     "Name": name,
        #     "SPIC": ikpu,
        #     "PackageCode": package_code,
        #     "Price": price * 100,
        #     # "Amount": amount, TODO: # amount should be get from order item product quantity # noqa
        #     "VAT": vat_amount * 100,
        #     "VATPercent": vat_percent,  # This should now be 12 from API or default
        #     "CommissionInf": {
        #         "TIN": inn,
        #     },
        # },

    #     if uid in final_result_dict:
    #         if price not in final_result_dict[uid]["prices"]:
    #             final_result_dict[uid]["prices"].append(price)
    #         if price not in final_result_dict[uid]["amount"]:
    #             final_result_dict[uid]["amount"].append(f"{amount}, штук  {price}, сум ")
                
    #     else:
    #         ProductType = item.get("ProductType", "")
    #         if isinstance(ProductType, list) and ProductType:
    #             ProductType = ProductType[0]
    #         else:
    #             ProductType = ProductType


    #         if ProductType == "Rx":
    #             ProductType = "Рецепт билан"
    #         elif ProductType == "ОТС":
    #             ProductType = "Рецептсиз"
    #         if product.name != name:
    #             product.name = name
    #             product.save()
    #         final_result_dict[uid] = {
    #             "uid": uid,
    #             "id": product.id,
    #             "name": name,
    #             "name_lower": name.lower(),
    #             "prices": [price],
    #             "class": category,
    #             "producer": item.get("Producer", ""),
    #             "country": item.get("Country", ""),
    #             "MNN": item.get("MNN", ""),
    #             "ReleaseForm": item.get("ReleaseForm", ""),
    #             "ProductType": ProductType,
    #             "ExpDate": item.get("ExpDate", ""),

    #             "amount": [f"{amount}, штук {price}, сум "],
    #             "image1": product.image1.url if product.image1 else "",
    #             "fiscal_items": fiscal_items,
    #         },

    # final_result = list(final_result_dict.values())

    # for item in final_result:
    #     category = item["class"]
    #     grouped_by_class.setdefault(category, []).append(item)

    # r.setex('final_result', 86400, json.dumps(final_result))
    # r.setex('products_by_class', 86400, json.dumps(grouped_by_class))

    # logger.info(f"Redis cache updated successfully! {datetime.datetime.now()},")
    


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


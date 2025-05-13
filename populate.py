import os
import django
import random
from django.core.files import File
from pathlib import Path

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Admin.settings')
django.setup()

# Import your models
from Product.models import Product, Category

product_ids = [	
    10024645,
	10024638,
	10024607,
	10024591,
	10024553,
	10024423,
	10024294,
	10024249,
	10024232,
	10024218,
	10024157,
	10024140,
	10023785,
	10023761,
	10023679,
	10023655,
	10023624,
	10000199,
	10000175,
	10000168,
	10000144,
	10000137,
	10000120,
	10000113,
	10000106,
	10000076,
	10000069,
	10000052,
	10000045,
	10000038,
	10024607,
    ]

product_names = [
    "Paracetamol",
    "Ibuprofen",
    "Aspirin",
    "Diclofenac",
    "Naproxen",
    "Amoxicillin",
    "Azithromycin",
    "Ciprofloxacin",
    "Doxycycline",
    "Cephalexin",
    "Acyclovir",
    "Oseltamivir",
    "Remdesivir",
    "Valacyclovir",
    "Lamivudine",
    "Cetirizine",
    "Loratadine",
    "Diphenhydramine",
    "Fexofenadine",
    "Chlorpheniramine",
    "Omeprazole",
    "Pantoprazole",
    "Ranitidine",
    "Loperamide",
    "Domperidone",
    "Metformin",
    "Amlodipine",
    "Atorvastatin",
    "Salbutamol",
    "Levothyroxine",
]

product_image = r"C:\Users\Shukurillo\Pictures\akmal farm\i_H2fGCjb.jpg"

def populate_products():
    print("Populating the database with products...")
    
    existing_uids = set(Product.objects.values_list('uid', flat=True))
    
    added_count = 0
    
    # Verify the image file exists
    image_path = Path(product_image)
    if not image_path.exists():
        print(f"Warning: Image file not found at {product_image}")
        print("Products will be created without images")
        has_image = False
    else:
        has_image = True
    
    for i, (uid, name) in enumerate(zip(product_ids, product_names)):
        if uid in existing_uids:
            print(f"Product with UID {uid} already exists, skipping...")
            continue
            
        info = f"{name} - dori vositasi. {random.choice(['Tabletka', 'Kapsula', 'Suyuqlik', 'Malham'])} shaklidagi dori."
        
        # Create the product first
        product = Product(
            uid=uid,
            info=f"{name}: {info}"
        )
        product.save()
        
        # Add image if available
        if has_image:
            try:
                with open(product_image, 'rb') as img_file:
                    # Add the image
                    product.image1.save(
                        f"{name.lower().replace(' ', '_')}.jpg",
                        File(img_file),
                        save=True
                    )
                print(f"Added product: {name} (UID: {uid}) with image")
            except Exception as e:
                print(f"Error adding image for {name}: {e}")
                print(f"Added product: {name} (UID: {uid}) without image")
        else:
            print(f"Added product: {name} (UID: {uid}) without image")
            
        added_count += 1
    
    print(f"Added {added_count} new products to the database.")

if __name__ == "__main__":
    populate_products()
    print("Database population completed!")


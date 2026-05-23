# TrendLab Clothing Store

A sample clothing e-commerce website built with Python, Flask, HTML, CSS, JavaScript, and a Java utility placeholder.

## Features

- Homepage with featured collections and products
- Category pages with filters for size, color, fabric, and price
- Product detail pages with size chart, availability, and add-to-cart
- Cart and checkout flow with order management
- Customization page with design upload preview and style options
- User account section with login/signup support
- Admin dashboard for sales analytics and orders
- Wishlist/recommendation endpoints and coupon support
- Java placeholder module for additional customization processing

## Run Locally

1. Install Python requirements:

```powershell
cd d:\document\python\clothing_store
python -m pip install -r requirements.txt
```

2. Start the Flask app:

```powershell
python app.py
```

3. Open the site in your browser:

```text
http://127.0.0.1:5000
```

## Project Structure

- `app.py` - main Flask backend
- `templates/` - HTML templates
- `static/css/` - styling
- `static/js/` - frontend interaction scripts
- `data/products.json` - sample product data
- `java/CustomizationProcessor.java` - Java placeholder for customization logic

## Notes

- The project uses in-memory data stores for demo purposes.
- Customize the product catalog and add real payment gateway integration for production.

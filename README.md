# Tempio di Grotalek

## E-commerce Store

> 🌐 Try the website on: 
> [Tempio di Grotalek](https://tempio-di-grotalek.up.railway.app/)

**Tempio di Grotalek** is a website designed to offer an online shopping experience.
The main goal is to emulate an e-commerce site for a store selling board games, cards, manuals, and miniatures.

---

## Architecture and technologies

The app is based on an MVC architecture: Django governs the business logic
and interactions with the PostgreSQL database, while Bootstrap 5 guarantees
a responsive interface accessible from desktop and mobile. Railway ensures
continuous deployment, with integrated rollback and monitoring, and Cloudinary
allows fast and secure uploads of event images.

---

## Feature overview

- **Category navigation**: Easily browse products divided by thematic categories, thanks to a clear structure and dynamic filters.
- **Advanced search**: Quickly find products through a search bar that filters by name or category.
- **Persistent cart**: Add, edit, and keep products in the cart even after login, with support for variants and quantities.
- **Order management**: View the history and details of your orders directly from your user profile.
- **User profile**: Update personal data, manage addresses, and review your past orders.
- **Authentication and roles**: Registration, secure login, and session management. Upon registration, a confirmation email is sent to the user for account verification. A password recovery email is also available. Role system (user, manager, admin) for access to advanced features.
- **Admin area**: Panel to manage products, categories, stock, and orders, with the ability to add variants and images.
- **Secure checkout**: Order summary, tax calculation, and purchase confirmation with order status management.

---

## User actions

- **Homepage browsing**: The user lands on the homepage and can browse products or categories.
- **Product discovery**: The user navigates by category or uses the search bar to find specific products.
- **Product details**: By clicking on a product, the user views detailed information, available variants, and images.
- **Cart management**: The user adds products (with selected variants and quantities) to the cart, which is persistent across sessions.
- **Authentication**: To proceed with the purchase, the user registers or logs in (with role-based access if needed). Upon registration, a confirmation email is sent for account verification. A password recovery email is also available.
- **Checkout**: The user reviews the cart, enters shipping details, and confirms the order.
- **Order confirmation**: The user receives a summary and can track the order status from their profile.
- **Profile and order history**: The user can update personal data, change profile picture, view past orders, and manage addresses.
- **Admin/Manager flow**: Users with elevated roles can access the admin area to manage products, categories, stock and product's variations.

---

# Disclaimer

## Project files

To view and download the source files with populated database and the necessary resources go to this [realease](https://github.com/Eros-Pinzani/E-commerce/releases/tag/local-website).
> [Tempio di Grotalek - source files](https://github.com/Eros-Pinzani/E-commerce/releases/tag/local-website)

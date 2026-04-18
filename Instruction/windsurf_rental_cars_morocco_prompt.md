# Full Windsurf Prompt — Django Rental Cars Website (Morocco)

## PROJECT OVERVIEW

Build a **premium rental car booking/management website for the Moroccan market** using:

- **Backend:** Django 5+
- **Frontend:** Django Templates
- **CSS:** Tailwind CSS
- **Interactivity:** Alpine.js
- **Database:** PostgreSQL
- **Deployment Ready:** Docker + Nginx + Gunicorn
- **Admin:** Custom Dashboard (NOT default Django admin for business management)
- **Languages:** French / Arabic ready (multilingual architecture)
- **SEO Optimized**
- **Mobile First Responsive Design**

The website will allow admins to manage rental cars, availability, booking periods, categories, and statistics while providing visitors with real-time visibility into fleet availability.

Design should be:

- Premium / Modern / Trustworthy
- Clean Booking Experience
- Moroccan Market Friendly
- Fast and Mobile Optimized

---

## DEVELOPMENT PHASES

### PHASE 1 — PROJECT INITIALIZATION

Create the Django project architecture professionally.

#### Requirements

- create a virtual environment venv
- Setup Django project with modular architecture
- Configure PostgreSQL
- Configure TailwindCSS with Django integration
- Configure Alpine.js globally
- Setup base templates and layout system
- Configure static/media files
- Environment variables with `.env`
- Production-ready settings split:
  - base.py
  - dev.py
  - prod.py

#### Suggested Structure

```bash
project/
│
├── apps/
│   ├── core/
│   ├── fleet/
│   ├── bookings/
│   ├── dashboard/
│   ├── users/
│   └── analytics/
│
├── templates/
├── static/
├── media/
└── config/
```

---

### PHASE 2 — CORE DATABASE MODELS

Create scalable rental fleet models.

#### Car Category Model

Fields:

- name
- slug
- icon/image
- description
- is_active

#### Brand Model

Fields:

- name
- slug
- logo

#### Rental Car Model

Fields:

- title
- slug
- category (FK)
- brand (FK)
- model_name
- year
- transmission
- fuel_type
- seats
- doors
- luggage_capacity
- color
- mileage
- registration_city
- daily_price
- weekly_price
- monthly_price
- deposit_amount
- description
- featured (bool)
- active (bool)
- availability_status:
  - Available
  - Reserved
  - Rented
  - Maintenance
- available_from (datetime/date)
- created_at
- updated_at

#### Car Images Model

Fields:

- car (FK)
- image
- alt_text
- is_featured
- order

#### Car Feature Model

Many-to-many with Rental Car.

Examples:

- GPS
- Bluetooth
- Rear Camera
- CarPlay
- Leather Seats
- Child Seat Compatible
- Cruise Control

---

### PHASE 3 — AVAILABILITY / BOOKING MANAGEMENT

Build booking and availability system.

#### Booking / Reservation Model

Fields:

- car (FK)
- customer_name
- customer_phone
- customer_email
- start_date
- end_date
- total_days
- total_price
- booking_status:
  - Pending
  - Confirmed
  - Cancelled
  - Completed
- notes
- created_at

#### Availability Logic

Implement logic to:

- Automatically detect unavailable periods
- Prevent double booking
- Show next available date
- Mark car as available/unavailable dynamically
- Calculate booking overlap properly

---

### PHASE 4 — PUBLIC WEBSITE FRONTEND

Build visitor-facing rental website.

#### Homepage Sections

- Hero Banner
- Search / Availability Filter
- Featured Rental Cars
- Available Now Cars
- Upcoming Available Cars
- Browse by Category
- Why Choose Us
- Testimonials
- Contact CTA

#### Cars Listing Page

Filters:

- Category
- Brand
- Price Range
- Transmission
- Fuel Type
- Seats
- Availability
- Date Available
- Search by Keyword

Features:

- Pagination
- Sorting:
  - Price Low/High
  - Availability Soonest
  - Newest
- Grid/List Toggle via Alpine.js

#### Car Detail Page

Include:

- Image Gallery / Slider
- Full Specifications
- Availability Status Badge
- Next Available Date
- Rental Pricing Table
- Included Features
- Rental Terms
- Similar Cars
- WhatsApp CTA

---

### PHASE 5 — WHATSAPP INQUIRY SYSTEM

Implement dynamic WhatsApp contact flow.

#### Requirements

Generate direct WhatsApp link containing:

- Selected Car Name
- Rental Dates (if chosen)
- Availability Info
- Pre-filled Inquiry Message

Example Message:

Hello, I'm interested in renting the Toyota Corolla 2024 from 10/05/2026 to 15/05/2026. Is it available?

---

### PHASE 6 — CUSTOM ADMIN DASHBOARD

Build business management dashboard.

#### Dashboard Overview Cards

- Total Cars
- Available Cars
- Reserved Cars
- Rented Cars
- Maintenance Cars
- Total Bookings
- Upcoming Returns
- Revenue Estimate

#### Fleet Management

Admin can:

- Add/Edit/Delete Cars
- Upload Multiple Images
- Reorder Images
- Toggle Featured
- Set Availability
- Mark Maintenance
- Set Available From Date

#### Booking Management

Admin can:

- View All Reservations
- Confirm/Cancel Bookings
- Mark Returned
- Track Upcoming Returns
- Add Manual Reservations

#### Category / Brand Management

CRUD for:

- Categories
- Brands

---

### PHASE 7 — ANALYTICS & STATISTICS

Create analytics dashboard.

#### Charts / Stats

- Bookings Per Month
- Revenue Per Month
- Most Rented Cars
- Fleet Utilization Rate
- Availability Distribution
- Upcoming Reservation Calendar
- Popular Categories

Use:

- Chart.js or ApexCharts

---

### PHASE 8 — SEO OPTIMIZATION

Implement SEO best practices.

- SEO-friendly slugs
- Dynamic meta tags
- OpenGraph tags
- Structured data
- Sitemap.xml
- Robots.txt
- Canonical URLs
- Breadcrumbs

---

### PHASE 9 — MULTILINGUAL READY

Prepare architecture for:

- French
- Arabic
- English future support

Requirements:

- Django i18n enabled
- RTL support for Arabic
- Language Switcher

---

### PHASE 10 — UI/UX DESIGN SYSTEM

#### Style Direction

- Premium Rental Fleet Look
- Professional Corporate Feel
- High Contrast / Clean Layout
- Elegant Typography
- Smooth Hover Effects
- Strong CTA Buttons

#### Suggested Color Palette

Primary: #0F172A  
Secondary: #1E293B  
Accent: #F59E0B  
Highlight: #22C55E  
Background: #F8FAFC  
Text: #0F172A  
Muted: #64748B  

---

### PHASE 11 — PRODUCTION READINESS

- Secure settings
- Logging
- Error pages (404 / 500)
- Performance optimization
- Query optimization
- Caching ready
- Production Docker setup
- Cloud-ready static/media handling

---

## DEVELOPMENT RULES

### Django Best Practices

- Use Class-Based Views when appropriate
- Keep business logic in services/helpers
- Use Forms / ModelForms professionally
- Use custom managers/querysets
- Optimize queries with select_related/prefetch_related

### Frontend Standards

- Tailwind utility-first reusable components
- Alpine.js only for lightweight interactivity
- Responsive-first development

### Code Quality

- Modular reusable apps
- Clean architecture
- Well-commented code
- Production-grade standards

---

## FINAL OUTPUT EXPECTATION

Build the project phase-by-phase.

After completing each phase:

1. Explain what was built
2. Show folder/file changes
3. Wait for confirmation before moving to next phase

Do NOT generate everything at once.

Proceed sequentially like a senior software architect.

---

## OPTIONAL BONUS FEATURES

- Calendar Availability Picker
- Seasonal Pricing Rules
- Discount / Coupon System
- Driver Add-on Option
- Airport Pickup Option
- Email Booking Confirmations
- PDF Rental Agreement Generator

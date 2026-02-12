{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}OceanBasket - Fresh Seafood Delivery{% endblock %}</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=Playfair+Display:wght@600;700;800&display=swap" rel="stylesheet">
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Custom CSS -->
    <style>
        :root {
            /* Ocean Theme Colors */
            --ocean-primary: #0891b2;      /* Cyan 600 */
            --ocean-secondary: #0e7490;    /* Cyan 700 */
            --ocean-dark: #164e63;         /* Cyan 900 */
            --ocean-light: #cffafe;        /* Cyan 100 */
            --ocean-lighter: #ecfeff;      /* Cyan 50 */
            
            --coral: #f97316;              /* Orange 500 */
            --coral-dark: #ea580c;         /* Orange 600 */
            
            --sea-green: #10b981;          /* Emerald 500 */
            --sea-green-dark: #059669;     /* Emerald 600 */
            
            --sand: #fef3c7;               /* Amber 100 */
            --sand-dark: #fcd34d;          /* Amber 300 */
            
            --text-primary: #0f172a;       /* Slate 900 */
            --text-secondary: #475569;     /* Slate 600 */
            --text-light: #94a3b8;         /* Slate 400 */
            
            --white: #ffffff;
            --gray-50: #f8fafc;
            --gray-100: #f1f5f9;
            --gray-200: #e2e8f0;
            
            /* Shadows */
            --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
            --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
            --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
            
            /* Border Radius */
            --radius-sm: 0.375rem;
            --radius-md: 0.5rem;
            --radius-lg: 0.75rem;
            --radius-xl: 1rem;
            --radius-2xl: 1.5rem;
            
            /* Transitions */
            --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: var(--text-primary);
            line-height: 1.6;
            background: var(--gray-50);
            overflow-x: hidden;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Playfair Display', serif;
            font-weight: 700;
            line-height: 1.2;
            color: var(--ocean-dark);
        }
        
        /* ========== NAVBAR ========== */
        .navbar-ocean {
            background: var(--white);
            box-shadow: var(--shadow-md);
            padding: 1rem 0;
            position: sticky;
            top: 0;
            z-index: 1000;
            transition: var(--transition);
        }
        
        .navbar-ocean.scrolled {
            padding: 0.5rem 0;
            box-shadow: var(--shadow-lg);
        }
        
        .navbar-brand-ocean {
            font-family: 'Playfair Display', serif;
            font-weight: 800;
            font-size: 1.75rem;
            color: var(--ocean-primary);
            display: flex;
            align-items: center;
            gap: 0.75rem;
            text-decoration: none;
            transition: var(--transition);
        }
        
        .navbar-brand-ocean:hover {
            color: var(--ocean-secondary);
            transform: scale(1.02);
        }
        
        .brand-icon {
            width: 45px;
            height: 45px;
            background: linear-gradient(135deg, var(--ocean-primary), var(--ocean-secondary));
            border-radius: var(--radius-lg);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            box-shadow: var(--shadow-md);
        }
        
        .nav-link-ocean {
            color: var(--text-secondary);
            font-weight: 500;
            padding: 0.5rem 1rem !important;
            margin: 0 0.25rem;
            border-radius: var(--radius-md);
            transition: var(--transition);
            position: relative;
        }
        
        .nav-link-ocean:hover,
        .nav-link-ocean.active {
            color: var(--ocean-primary);
            background: var(--ocean-lighter);
        }
        
        .nav-link-ocean::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            width: 0;
            height: 2px;
            background: var(--ocean-primary);
            transition: var(--transition);
            transform: translateX(-50%);
        }
        
        .nav-link-ocean:hover::after {
            width: 60%;
        }
        
        /* Buttons */
        .btn-ocean-primary {
            background: linear-gradient(135deg, var(--ocean-primary), var(--ocean-secondary));
            color: var(--white);
            border: none;
            padding: 0.75rem 1.75rem;
            border-radius: var(--radius-lg);
            font-weight: 600;
            transition: var(--transition);
            box-shadow: var(--shadow-md);
            position: relative;
            overflow: hidden;
        }
        
        .btn-ocean-primary::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            transition: var(--transition);
        }
        
        .btn-ocean-primary:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
            color: var(--white);
        }
        
        .btn-ocean-primary:hover::before {
            left: 100%;
        }
        
        .btn-ocean-outline {
            background: transparent;
            color: var(--ocean-primary);
            border: 2px solid var(--ocean-primary);
            padding: 0.65rem 1.75rem;
            border-radius: var(--radius-lg);
            font-weight: 600;
            transition: var(--transition);
        }
        
        .btn-ocean-outline:hover {
            background: var(--ocean-primary);
            color: var(--white);
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }
        
        /* Cart Badge */
        .cart-badge {
            position: absolute;
            top: -8px;
            right: -8px;
            background: var(--coral);
            color: var(--white);
            font-size: 0.7rem;
            font-weight: 700;
            padding: 0.25rem 0.5rem;
            border-radius: 999px;
            box-shadow: var(--shadow-md);
        }
        
        /* ========== HERO SECTION ========== */
        .hero-ocean {
            background: linear-gradient(135deg, var(--ocean-lighter) 0%, var(--ocean-light) 100%);
            position: relative;
            overflow: hidden;
            padding: 5rem 0;
        }
        
        .hero-ocean::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320"><path fill="%230891b2" fill-opacity="0.05" d="M0,96L48,112C96,128,192,160,288,160C384,160,480,128,576,112C672,96,768,96,864,112C960,128,1056,160,1152,160C1248,160,1344,128,1392,112L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path></svg>') bottom center no-repeat;
            background-size: cover;
        }
        
        /* ========== PRODUCT CARDS ========== */
        .product-card-ocean {
            background: var(--white);
            border-radius: var(--radius-xl);
            overflow: hidden;
            box-shadow: var(--shadow-md);
            transition: var(--transition);
            height: 100%;
            display: flex;
            flex-direction: column;
        }
        
        .product-card-ocean:hover {
            transform: translateY(-8px);
            box-shadow: var(--shadow-xl);
        }
        
        .product-img-wrapper {
            position: relative;
            overflow: hidden;
            background: var(--gray-100);
            padding-top: 75%; /* 4:3 Aspect Ratio */
        }
        
        .product-img-ocean {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: var(--transition);
        }
        
        .product-card-ocean:hover .product-img-ocean {
            transform: scale(1.1);
        }
        
        .product-badge {
            position: absolute;
            top: 1rem;
            right: 1rem;
            padding: 0.4rem 0.9rem;
            border-radius: var(--radius-lg);
            font-weight: 600;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            box-shadow: var(--shadow-md);
        }
        
        .badge-fresh {
            background: linear-gradient(135deg, var(--sea-green), var(--sea-green-dark));
            color: var(--white);
        }
        
        .badge-sale {
            background: linear-gradient(135deg, var(--coral), var(--coral-dark));
            color: var(--white);
        }
        
        .product-content {
            padding: 1.5rem;
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        
        .product-category {
            color: var(--ocean-primary);
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
        }
        
        .product-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--ocean-dark);
            margin-bottom: 0.75rem;
            line-height: 1.4;
        }
        
        .product-description {
            color: var(--text-secondary);
            font-size: 0.9rem;
            margin-bottom: 1rem;
            flex: 1;
        }
        
        .product-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 1rem;
            border-top: 1px solid var(--gray-200);
        }
        
        .product-price {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--ocean-primary);
        }
        
        .product-price-unit {
            font-size: 0.85rem;
            color: var(--text-light);
            font-weight: 400;
        }
        
        .btn-add-cart {
            background: var(--ocean-primary);
            color: var(--white);
            border: none;
            padding: 0.6rem 1.2rem;
            border-radius: var(--radius-lg);
            font-weight: 600;
            transition: var(--transition);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .btn-add-cart:hover {
            background: var(--ocean-secondary);
            transform: scale(1.05);
            color: var(--white);
        }
        
        /* ========== FEATURES SECTION ========== */
        .feature-card {
            background: var(--white);
            padding: 2rem;
            border-radius: var(--radius-xl);
            text-align: center;
            transition: var(--transition);
            box-shadow: var(--shadow-sm);
            height: 100%;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: var(--shadow-lg);
        }
        
        .feature-icon {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, var(--ocean-lighter), var(--ocean-light));
            border-radius: var(--radius-xl);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1.5rem;
            font-size: 2rem;
            box-shadow: var(--shadow-md);
        }
        
        .feature-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--ocean-dark);
            margin-bottom: 0.75rem;
        }
        
        .feature-description {
            color: var(--text-secondary);
            font-size: 0.95rem;
        }
        
        /* ========== SECTION STYLING ========== */
        .section-ocean {
            padding: 5rem 0;
        }
        
        .section-title {
            font-size: 2.5rem;
            font-weight: 800;
            color: var(--ocean-dark);
            margin-bottom: 1rem;
            position: relative;
            display: inline-block;
        }
        
        .section-title::after {
            content: '';
            position: absolute;
            bottom: -10px;
            left: 0;
            width: 60px;
            height: 4px;
            background: linear-gradient(90deg, var(--ocean-primary), var(--coral));
            border-radius: 999px;
        }
        
        .section-subtitle {
            color: var(--text-secondary);
            font-size: 1.1rem;
            margin-bottom: 3rem;
        }
        
        /* ========== FOOTER ========== */
        .footer-ocean {
            background: linear-gradient(135deg, var(--ocean-dark) 0%, var(--ocean-secondary) 100%);
            color: var(--white);
            margin-top: 5rem;
            position: relative;
            overflow: hidden;
        }
        
        .footer-ocean::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--coral), var(--sea-green), var(--ocean-primary));
        }
        
        .footer-title {
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            color: var(--white);
        }
        
        .footer-link {
            color: rgba(255, 255, 255, 0.8);
            text-decoration: none;
            display: block;
            margin-bottom: 0.75rem;
            transition: var(--transition);
            font-size: 0.95rem;
        }
        
        .footer-link:hover {
            color: var(--white);
            padding-left: 5px;
        }
        
        .social-links {
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .social-link {
            width: 45px;
            height: 45px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: var(--radius-lg);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--white);
            text-decoration: none;
            transition: var(--transition);
            backdrop-filter: blur(10px);
        }
        
        .social-link:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-3px);
            color: var(--white);
        }
        
        .newsletter-form {
            display: flex;
            gap: 0.5rem;
            margin-top: 1rem;
        }
        
        .newsletter-input {
            flex: 1;
            padding: 0.75rem 1.25rem;
            border: 2px solid rgba(255, 255, 255, 0.2);
            background: rgba(255, 255, 255, 0.1);
            border-radius: var(--radius-lg);
            color: var(--white);
            backdrop-filter: blur(10px);
        }
        
        .newsletter-input::placeholder {
            color: rgba(255, 255, 255, 0.6);
        }
        
        .newsletter-input:focus {
            outline: none;
            border-color: var(--white);
            background: rgba(255, 255, 255, 0.15);
        }
        
        .newsletter-btn {
            padding: 0.75rem 1.5rem;
            background: var(--coral);
            border: none;
            border-radius: var(--radius-lg);
            color: var(--white);
            font-weight: 600;
            transition: var(--transition);
        }
        
        .newsletter-btn:hover {
            background: var(--coral-dark);
            transform: scale(1.05);
        }
        
        .footer-bottom {
            padding-top: 2rem;
            text-align: center;
            color: rgba(255, 255, 255, 0.7);
        }
        
        /* ========== UTILITIES ========== */
        .text-ocean {
            color: var(--ocean-primary);
        }
        
        .bg-ocean-light {
            background: var(--ocean-lighter);
        }
        
        .wave-divider {
            position: relative;
            margin: -1px 0;
        }
        
        /* ========== ANIMATIONS ========== */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .fade-in-up {
            animation: fadeInUp 0.6s ease-out;
        }
        
        /* ========== RESPONSIVE ========== */
        @media (max-width: 768px) {
            .section-title {
                font-size: 2rem;
            }
            
            .hero-ocean {
                padding: 3rem 0;
            }
            
            .navbar-brand-ocean {
                font-size: 1.5rem;
            }
            
            .brand-icon {
                width: 40px;
                height: 40px;
                font-size: 1.25rem;
            }
        }
    </style>
    
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-ocean">
        <div class="container">
            <a class="navbar-brand-ocean" href="{% url 'common:homepage' %}">
                <div class="brand-icon">
                    <i class="fas fa-fish"></i>
                </div>
                <span>OceanBasket</span>
            </a>
            
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto align-items-center">
                    <li class="nav-item">
                        <a class="nav-link-ocean active" href="{% url 'common:homepage' %}">
                            <i class="fas fa-home me-1"></i> Home
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link-ocean" href="#products">
                            <i class="fas fa-fish me-1"></i> Products
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link-ocean" href="{% url 'common:about' %}">
                            <i class="fas fa-info-circle me-1"></i> About
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link-ocean" href="{% url 'common:contact' %}">
                            <i class="fas fa-envelope me-1"></i> Contact
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link-ocean" href="{% url 'common:faq' %}">
                            <i class="fas fa-question-circle me-1"></i> FAQ
                        </a>
                    </li>
                    
                    {% if user.is_authenticated %}
                    <li class="nav-item">
                        <a class="nav-link-ocean" href="{% url 'common:dashboard' %}">
                            <i class="fas fa-tachometer-alt me-1"></i> Dashboard
                        </a>
                    </li>
                    <li class="nav-item ms-2">
                        <a class="nav-link-ocean position-relative" href="#">
                            <i class="fas fa-shopping-cart"></i>
                            <span class="cart-badge">3</span>
                        </a>
                    </li>
                    <li class="nav-item ms-2">
                        <a class="btn btn-ocean-outline btn-sm" href="#">
                            <i class="fas fa-sign-out-alt me-1"></i> Logout
                        </a>
                    </li>
                    {% else %}
                    <li class="nav-item ms-2">
                        <a class="btn btn-ocean-outline btn-sm" href="#">
                            <i class="fas fa-sign-in-alt me-1"></i> Login
                        </a>
                    </li>
                    <li class="nav-item ms-2">
                        <a class="btn btn-ocean-primary btn-sm" href="#">
                            <i class="fas fa-user-plus me-1"></i> Sign Up
                        </a>
                    </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <main>
        {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    <footer class="footer-ocean">
        <div class="container py-5">
            <div class="row g-4">
                <div class="col-lg-4 mb-4">
                    <div class="d-flex align-items-center mb-3">
                        <div class="brand-icon me-3">
                            <i class="fas fa-fish"></i>
                        </div>
                        <h3 class="footer-title mb-0">OceanBasket</h3>
                    </div>
                    <p style="color: rgba(255, 255, 255, 0.8);">
                        Fresh seafood delivered daily from the ocean to your kitchen. 
                        Premium quality, sustainable sourcing, and unbeatable freshness.
                    </p>
                    <div class="social-links mt-4">
                        <a href="#" class="social-link">
                            <i class="fab fa-facebook-f"></i>
                        </a>
                        <a href="#" class="social-link">
                            <i class="fab fa-instagram"></i>
                        </a>
                        <a href="#" class="social-link">
                            <i class="fab fa-twitter"></i>
                        </a>
                        <a href="#" class="social-link">
                            <i class="fab fa-youtube"></i>
                        </a>
                    </div>
                </div>
                
                <div class="col-lg-2 col-6 mb-4">
                    <h5 class="footer-title">Shop</h5>
                    <a href="#" class="footer-link">
                        <i class="fas fa-chevron-right me-2"></i>Fresh Fish
                    </a>
                    <a href="#" class="footer-link">
                        <i class="fas fa-chevron-right me-2"></i>Frozen Fish
                    </a>
                    <a href="#" class="footer-link">
                        <i class="fas fa-chevron-right me-2"></i>Shellfish
                    </a>
                    <a href="#" class="footer-link">
                        <i class="fas fa-chevron-right me-2"></i>Premium Cuts
                    </a>
                    <a href="#" class="footer-link">
                        <i class="fas fa-chevron-right me-2"></i>Special Offers
                    </a>
                </div>
                
                <div class="col-lg-2 col-6 mb-4">
                    <h5 class="footer-title">Support</h5>
                    <a href="{% url 'common:contact' %}" class="footer-link">
                        <i class="fas fa-chevron-right me-2"></i>Contact Us
                    </a>
                    <a href="{% url 'common:faq' %}" class="footer-link">
                        <i class="fas fa-chevron-right me-2"></i>FAQ
                    </a>
                    <a href="#" class="footer-link">
                        <i class="fas fa-chevron-right me-2"></i>Shipping Info
                    </a>
                    <a href="#" class="footer-link">
                        <i class="fas fa-chevron-right me-2"></i>Returns
                    </a>
                    <a href="#" class="footer-link">
                        <i class="fas fa-chevron-right me-2"></i>Track Order
                    </a>
                </div>
                
                <div class="col-lg-4 mb-4">
                    <h5 class="footer-title">Stay Updated</h5>
                    <p style="color: rgba(255, 255, 255, 0.8);">
                        Subscribe to get special offers, free recipes, and updates on new arrivals.
                    </p>
                    <form class="newsletter-form">
                        <input type="email" class="newsletter-input" placeholder="Your email address">
                        <button type="submit" class="newsletter-btn">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </form>
                    <div class="mt-4" style="color: rgba(255, 255, 255, 0.8);">
                        <i class="fas fa-phone me-2"></i> +91 9876543210<br>
                        <i class="fas fa-envelope me-2"></i> hello@oceanbasket.com
                    </div>
                </div>
            </div>
            
            <div class="footer-bottom">
                <p class="mb-0">
                    &copy; 2024 OceanBasket. All rights reserved. | 
                    <a href="#" class="footer-link d-inline">Privacy Policy</a> | 
                    <a href="#" class="footer-link d-inline">Terms of Service</a>
                </p>
            </div>
        </div>
    </footer>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Custom JS -->
    <script>
        // Navbar scroll effect
        window.addEventListener('scroll', function() {
            const navbar = document.querySelector('.navbar-ocean');
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
        
        // Smooth scroll for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                const href = this.getAttribute('href');
                if (href !== '#' && document.querySelector(href)) {
                    e.preventDefault();
                    document.querySelector(href).scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            });
        });
    </script>
    
    {% block extra_js %}{% endblock %}
</body>
</html>
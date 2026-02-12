(function($) {
  "use strict";

  /**
   * Preloader - Fixed for Django + Production
   * MAX 3 second wait, then FORCE show content
   */
  var initPreloader = function() {
    console.log('🎯 Preloader starting...');
    
    // Add preloader class immediately
    $('body').addClass('preloader-site');
    
    // Hide after 3 seconds MAX (emergency fallback)
    var preloaderTimeout = setTimeout(function() {
      console.log('⏰ Preloader timeout - forcing hide');
      hidePreloader();
    }, 3000);
    
    // Also hide on proper window load
    $(window).on('load', function() {
      console.log('✅ Window loaded - hiding preloader');
      clearTimeout(preloaderTimeout);
      hidePreloader();
    });
    
    function hidePreloader() {
      $('.preloader-wrapper').fadeOut(500, function() {
        $('body').removeClass('preloader-site');
        console.log('✅ Preloader hidden');
      });
    }
  };

  /**
   * Swiper Carousels - Safe initialization
   */
  var initSwiper = function() {
    if (typeof Swiper === 'undefined') {
      console.warn('❌ Swiper not loaded - skipping carousels');
      return;
    }
    
    console.log('🔄 Initializing Swiper carousels...');

    // Main hero swiper
    if (document.querySelector('.main-swiper')) {
      new Swiper('.main-swiper', {
        speed: 500,
        pagination: { el: '.swiper-pagination', clickable: true },
        loop: true,
        autoplay: { delay: 5000 }
      });
    }

    // Category carousel
    if (document.querySelector('.category-carousel')) {
      new Swiper('.category-carousel', {
        slidesPerView: 6,
        spaceBetween: 30,
        speed: 500,
        navigation: {
          nextEl: '.category-carousel-next',
          prevEl: '.category-carousel-prev'
        },
        breakpoints: {
          0: { slidesPerView: 2, spaceBetween: 15 },
          768: { slidesPerView: 3, spaceBetween: 20 },
          991: { slidesPerView: 4, spaceBetween: 25 },
          1200: { slidesPerView: 5, spaceBetween: 30 },
          1500: { slidesPerView: 6, spaceBetween: 30 }
        }
      });
    }

    // Brand carousel
    if (document.querySelector('.brand-carousel')) {
      new Swiper('.brand-carousel', {
        slidesPerView: 4,
        spaceBetween: 30,
        speed: 500,
        navigation: {
          nextEl: '.brand-carousel-next',
          prevEl: '.brand-carousel-prev'
        },
        breakpoints: {
          0: { slidesPerView: 2, spaceBetween: 15 },
          768: { slidesPerView: 2, spaceBetween: 20 },
          991: { slidesPerView: 3, spaceBetween: 25 },
          1500: { slidesPerView: 4, spaceBetween: 30 }
        }
      });
    }

    // Products carousel
    if (document.querySelector('.products-carousel')) {
      new Swiper('.products-carousel', {
        slidesPerView: 5,
        spaceBetween: 30,
        speed: 500,
        navigation: {
          nextEl: '.products-carousel-next',
          prevEl: '.products-carousel-prev'
        },
        breakpoints: {
          0: { slidesPerView: 1, spaceBetween: 10 },
          768: { slidesPerView: 3, spaceBetween: 20 },
          991: { slidesPerView: 4, spaceBetween: 25 },
          1500: { slidesPerView: 5, spaceBetween: 30 }
        }
      });
    }
    
    console.log('✅ Swiper carousels initialized');
  };

  /**
   * Product Quantity Controls - Event Delegation
   */
  var initProductQty = function() {
    $(document).off('click.qty-controls').on('click.qty-controls', '.quantity-right-plus', function(e) {
      e.preventDefault();
      e.stopPropagation();
      var $input = $(this).closest('.input-group, .product-qty').find('input[type="number"], input#quantity');
      if ($input.length) {
        var current = parseInt($input.val()) || 1;
        $input.val(Math.max(1, current + 1)).trigger('change');
      }
    });

    $(document).off('click.qty-controls').on('click.qty-controls', '.quantity-left-minus', function(e) {
      e.preventDefault();
      e.stopPropagation();
      var $input = $(this).closest('.input-group, .product-qty').find('input[type="number"], input#quantity');
      if ($input.length) {
        var current = parseInt($input.val()) || 1;
        if (current > 1) {
          $input.val(current - 1).trigger('change');
        }
      }
    });
    
    console.log('✅ Product quantity controls ready');
  };

  /**
   * Jarallax Parallax - Safe fallback
   */
  var initJarallax = function() {
    if (typeof jarallax === 'undefined') {
      console.warn('❌ Jarallax not loaded - skipping parallax effects');
      return;
    }
    
    jarallax(document.querySelectorAll('.jarallax'), {
      speed: 0.2
    });
    
    console.log('✅ Jarallax parallax initialized');
  };

  /**
   * Chocolat Lightbox - Safe fallback
   */
  var initChocolat = function() {
    if (typeof Chocolat === 'undefined') {
      console.warn('❌ Chocolat not loaded - skipping lightbox');
      return;
    }
    
    Chocolat(document.querySelectorAll('.image-link'), {
      imageSize: 'contain',
      loop: true,
      setIndex: 1
    });
    
    console.log('✅ Chocolat lightbox initialized');
  };

  /**
   * Wishlist Toggle
   */
  var initWishlist = function() {
    $(document).on('click', '.btn-wishlist', function(e) {
      e.preventDefault();
      var $btn = $(this);
      $btn.toggleClass('active');
      
      if ($btn.hasClass('active')) {
        $btn.find('use').attr('xlink:href', '#heart');
      } else {
        $btn.find('use').attr('xlink:href', '#heart-outline');
      }
    });
  };

  /**
   * Mobile Menu Toggle
   */
  var initMobileMenu = function() {
    $('.navbar-toggler').on('click', function() {
      $('.offcanvas-navbar').toggleClass('show');
    });
  };

  /**
   * MAIN INITIALIZATION - Production Ready
   */
  $(document).ready(function() {
    console.log('🚀 Django E-commerce JS starting...');
    
    // 1. Preloader FIRST (critical)
    initPreloader();
    
    // 2. Wait 100ms for DOM stability, then init everything
    setTimeout(function() {
      initSwiper();
      initProductQty();
      initWishlist();
      initMobileMenu();
      initJarallax();
      initChocolat();
      
      console.log('✅ All components loaded successfully!');
    }, 100);
  });

  // Window resize handler
  $(window).on('resize', function() {
    // Re-init swipers on resize if needed
    if (typeof Swiper !== 'undefined') {
      // Swiper handles resize automatically
    }
  });

})(jQuery);

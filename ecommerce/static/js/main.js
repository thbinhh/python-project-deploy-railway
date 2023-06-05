(function ($) {
    "use strict";
    
    // Dropdown on mouse hover
    $(document).ready(function () {
        function toggleNavbarMethod() {
            if ($(window).width() > 992) {
                $('.navbar .dropdown').on('mouseover', function () {
                    $('.dropdown-toggle', this).trigger('click');
                }).on('mouseout', function () {
                    $('.dropdown-toggle', this).trigger('click').blur();
                });
            } else {
                $('.navbar .dropdown').off('mouseover').off('mouseout');
            }
        }
        toggleNavbarMethod();
        $(window).resize(toggleNavbarMethod);

        var selectedItems = [];
        // Event handler for checkbox change
        $('input[name="cart_item_checkbox"]').change(function() {
            var itemId = $(this).val();
            var secondValue = $(this).data('second-value');

            if ($(this).is(':checked')) {
                // Checkbox is checked, add the item ID and second value to the selectedItems array
                selectedItems.push({ itemId: itemId, secondValue: secondValue });
            } else {
                // Checkbox is unchecked, remove the item ID from the selectedItems array
                var index = selectedItems.findIndex(item => item.itemId === itemId);
                if (index !== -1) {
                selectedItems.splice(index, 1);
                }
            }

            console.log(selectedItems); // For debugging, you can remove this line

            $('#selectedItems').val(JSON.stringify(selectedItems));
        });

    });
    
    
    // Back to top button
    $(window).scroll(function () {
        if ($(this).scrollTop() > 100) {
            $('.back-to-top').fadeIn('slow');
        } else {
            $('.back-to-top').fadeOut('slow');
        }
    });

    $('.back-to-top').click(function () {
        $('html, body').animate({scrollTop: 0}, 1500, 'easeInOutExpo');
        return false;
    });


    // Vendor carousel
    $('.vendor-carousel').owlCarousel({
        loop: true,
        margin: 29,
        nav: false,
        autoplay: true,
        smartSpeed: 1000,
        responsive: {
            0:{
                items:2
            },
            576:{
                items:3
            },
            768:{
                items:4
            },
            992:{
                items:5
            },
            1200:{
                items:6
            }
        }
    });


    // Related carousel
    $('.related-carousel').owlCarousel({
        loop: true,
        margin: 29,
        nav: false,
        autoplay: true,
        smartSpeed: 1000,
        responsive: {
            0:{
                items:1
            },
            576:{
                items:2
            },
            768:{
                items:3
            },
            992:{
                items:4
            }
        }
    });


    // Product Quantity
    $('.quantity button').on('click', function () {
        var button = $(this);
        var oldValue = button.parent().parent().find('input').val();
        var id = $(this).data('id');
        var price = $(this).data('price');
        var quantity = parseInt(oldValue);
        var priceTd = $('#price_' + id);


        if (button.hasClass('btn-plus')) {
            var newVal = parseFloat(oldValue) + 1;
            var totalPrice = price * newVal;
            priceTd.html(totalPrice);
        } else {
            if (oldValue > 1) {
                var newVal = parseFloat(oldValue) - 1;
                var totalPrice = price * newVal;
                priceTd.html(totalPrice);
            } else {
                newVal = 1;
                var totalPrice = price;
                priceTd.html(totalPrice);
            }
        }
        var inputField = button.parent().parent().find('input');
        inputField.val(newVal);
        inputField.attr('value', newVal);
    });

    $('#checkout_button').on('click', function () {
        document.getElementById('cart_form').submit();
    });


    $('#filter_button').on('click', function () {
        document.getElementById('filter-form').submit();
    });

    $('#checkout_button').on('click', function() {
        $('#cart_form').attr('action', '/checkout').submit();
    });

    $('#paypal_button').on('click', function() {
        $('#cart_form').attr('action', '/checkout-paypal').submit();
    });

    $('#billing_form').on('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission
    
        // Retrieve form data
        var quantities = $(this).find('input[name="quantities[]"]').map(function() {
            return $(this).val();
        }).get();
    
        var product_ids = $(this).find('input[name="product_id[]"]').map(function() {
            return $(this).val();
        }).get();
    
        var cart_ids = $(this).find('input[name="cart_id[]"]').map(function() {
            return $(this).val();
        }).get();
    
        var coupon_id = $(this).find('input[name="couponid"]').val();
        var email = $(this).find('input[name="email"]').val();
        var phone = $(this).find('input[name="phone"]').val();
        var diachi = $(this).find('input[name="diachi"]').val();
        var huyen = $(this).find('input[name="huyen"]').val();
        var tinh = $(this).find('input[name="tinh"]').val();
    
        // Create data object for AJAX request
        var formData = {
            'quantities': quantities,
            'product_ids': product_ids,
            'cart_ids': cart_ids,
            'coupon_id': coupon_id,
            'email': email,
            'phone': phone,
            'diachi': diachi,
            'huyen': huyen,
            'tinh': tinh
        };

    
        // Save the formDataString to the session
        document.cookie = 'form_data=' + JSON.stringify(formData) + '; path=/';

        $('#billing_form').attr('action', 'https://www.sandbox.paypal.com/cgi-bin/webscr');
        $('#billing_form').get(0).submit();
   
    });
    

})(jQuery);


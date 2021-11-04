document.addEventListener("DOMContentLoaded", function () {
    var clicks = 0;
    $('#egg').on("mousedown", function () {
        if (clicks > 50) {
            return;
        }
        if (clicks > 42) {
            $(this).toggleClass('fas far').toggleClass('fa-egg fa-dizzy');
        }
        else if (clicks > 39) {
            $(this).toggleClass('fas far').toggleClass('fa-egg fa-angry');
        }
        else if (clicks > 36) {
            $(this).toggleClass('fas far').toggleClass('fa-egg fa-frown-open');
        }
        else if (clicks > 33) {
            $(this).toggleClass('fas far').toggleClass('fa-egg fa-frown');
        }
        else if (clicks > 29) {
            $(this).toggleClass('fas far').toggleClass('fa-egg fa-flushed');
        }
        else if (clicks > 26) {
            $(this).toggleClass('fas far').toggleClass('fa-egg fa-meh-blank');
        }
        else if (clicks > 23) {
            $(this).toggleClass('fas far').toggleClass('fa-egg fa-meh');
        }
        else if (clicks > 20) {
            $(this).toggleClass('fas far').toggleClass('fa-egg fa-grin-beam-sweat');
        }
        else if (clicks > 13) {
            $(this).toggleClass('fas far').toggleClass('fa-egg fa-grin-beam');
        }
        else if (clicks > 10) {
            $(this).toggleClass('fas far').toggleClass('fa-egg fa-grin');
        }
        else if (clicks > 5) {
            $(this).toggleClass('fas far').toggleClass('fa-egg fa-smile');
        }
        else {
            $(this).toggleClass('fas far').toggleClass('fa-egg fa-smile-wink');
        }
        clicks = clicks + 1;
    }).on("mouseup", function () {
        if (clicks >= 50) {
            return;
        }
        $(this).removeClass('fa-smile-wink').removeClass('fa-smile').removeClass('fa-grin');
        $(this).removeClass('fa-grin-beam').removeClass('fa-grin-beam-sweat').removeClass('fa-meh');
        $(this).removeClass('fa-meh-blank').removeClass('fa-flushed').removeClass('fa-frown');
        $(this).removeClass('fa-frown-open').removeClass('fa-angry').removeClass('fa-dizzy');
        $(this).toggleClass('far fas');
        $(this).addClass('fa-egg');
    });
});


/**
 *
 * Created by nreed on 11/17/14.
 */
$(document).ready(function () {
    $("li").find("a[href='#advanced']").one("click", function() {
        setTimeout(function () {
            window.xmleditor.mirror.refresh();
        });
    });

    $("form").bind("keypress", function(e) {
        // Enter key.
        if (e.keyCode == 13) {
            e.preventDefault();
        }
    });
});
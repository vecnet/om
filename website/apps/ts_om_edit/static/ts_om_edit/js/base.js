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

    $("#further-info").html($("#wiki-info").html());
});
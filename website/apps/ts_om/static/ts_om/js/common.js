/**
 * Created by nreed on 11/12/14.
 */

$(function() {
    var csrfToken = getCookie('csrftoken');

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrfToken);
            }
        }
    });
});

String.prototype.capitalize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
};

function getCookie(name) {
    var cookieVal = null;

    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');

        for (var i = 0; i < cookies.length; i++) {
            var cookie = $.trim(cookies[i]);

            if (cookie.substring(0, name.length + 1) == name + "=") {
                cookieVal = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }

    return cookieVal;
}

function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

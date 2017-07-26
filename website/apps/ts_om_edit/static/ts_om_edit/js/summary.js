var deleteData = Object;

$(function() {
    $("#summary").addClass("active");

    var delObj = $(".delete");
    deleteData = delObj.data();

    $("#delete").click(function() {
        var id = $("#modal-scenario-id").val();
        var deleteMsg =  $("#delete-message");

        deleteMsg.hide();
        deleteMsg.empty();

        var deleteType = deleteData.type;
        var typeStr = deleteType.substr(0, deleteType.length-1);
        var newDeleteType = (deleteType == "restore") ? "delete" : "restore";

        $.post("/ts_om/deleteScenario/", { scenario_ids: JSON.stringify([id]) }, function (data) {
            if (data != null) {
                if (data.ok) {
                    var confirmObj = $("#confirm");

                    deleteMsg.removeClass("alert-error");
                    deleteMsg.addClass("alert-success");
                    deleteMsg.append("<p>Simulation " + typeStr + "ed.</p>");
                    deleteMsg.show();

                    if (deleteType == "delete")
                        $("#name, #desc").attr("disabled", "disabled");
                    else
                        $("#name, #desc").removeAttr("disabled");

                    deleteData.type = newDeleteType;
                    deleteData.originalTitle = deleteData.originalTitle.replace(deleteType.capitalize(), newDeleteType.capitalize());

                    delObj.attr("data-type", deleteData.type);
                    delObj.attr("data-original-title", deleteData.originalTitle);
                    delObj.text(newDeleteType.capitalize());

                    confirmHeader = confirmObj.find(".modal-header > h3");
                    confirmBody = confirmObj.find(".modal-body > p");
                    confirmHeader.html(confirmHeader.html().replace(deleteType.capitalize(), newDeleteType.capitalize()));
                    confirmBody.html(confirmBody.html().replace(deleteType, newDeleteType));
                    $("#delete").text(newDeleteType.capitalize());
                } else {
                    deleteMsg.removeClass("alert-success");
                    deleteMsg.addClass("alert-error");
                    deleteMsg.append("<p>Error " + typeStr + "ing simulation.</p>");
                    deleteMsg.show();
                }
            }
        }, "json").fail(function(jqXHR, textStatus, errorThrown) {
            deleteMsg.append("<p>Error " + typeStr + "ing simulation.</p>");
            deleteMsg.show();
        });
    });

    delObj.click(function() {
        $("#modal-scenario-id").val(deleteData.id);
    });

    window.xmleditor.mirror.options.readOnly = $("#simulation-id").val() > 0;
    $(".advanced-tab-extra-text").hide();

    var modeTabsObj = $("#mode-tabs");
});


/**
 * Created by nreed on 11/18/14.
 */

var deleteData = Object;

$(function() {
    $("#summary").addClass("active");
    var sim_id = parseInt($("#simulation-id").val());
    var delObj = $(".delete");
    deleteData = delObj.data();

    if (sim_id > -1) {
        $("#monitoring").hide();
        $("#demography").hide();
        $("#healthsystem").hide();
        $("#entomology").hide();
        $("#interventions").hide();
        $("#deployments").hide();
    }

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

    $("#id_name").change(function (e) {
        $xml = null;

        try {
            $xml = getScenarioXml();
        } catch (err) {
            return false;
        }

        $scenario = $xml.find("om\\:scenario");

        if ($scenario != null) {
            $scenario.attr("name", $(this).val());

            updateEditorXml($xml);
        }
    });

    $('a[data-toggle="tab"]').on("shown", function(e) {
        if ($(this).attr("href") == "#simple") {
            $xml = null;

            try {
                $xml = getScenarioXml();
            } catch (err) {
                return false;
            }

            $scenario = $xml.find("om\\:scenario");

            if ($scenario != null) {
                var name = $scenario.attr("name");

                $("#id_name").val(name);
            }
        }
    });

    window.xmleditor.mirror.options.readOnly = $("#simulation-id").val() > 0;
    $(".advanced-tab-extra-text").hide();
    $(".discard-changes").show();
});

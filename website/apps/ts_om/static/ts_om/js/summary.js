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

    $("#save-scenario-xml").click(function(){
        scenario_id = $("#save-scenario-xml").attr("data-scenario-id");
        // Get XML from CodeMirror edit area
        xml =  window.xmleditor.getValue();
       $.post("/ts_om/update/", {scenario_id: scenario_id, xml:xml}, function(data){
            alert("Successfully updated XML");
       }).fail(function(jqXHR, textStatus, errorThrown) {
           alert("Can't update XML: " + errorThrown);
       });
    });

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

    $("#save-scenario-summary-page").click(function () {
        var data = $("form").serializeArray();
        var save = true;

        data.push({name: 'save', value: save});

        $.post(window.location.href, data, function(data) {
            if (data.hasOwnProperty("success") && data.success) {
                $(".save-scenario").trigger("click");
            }
        }, "json").fail(function(jqXHR, textStatus, errorThrown) {
        });
    });

    window.xmleditor.mirror.options.readOnly = $("#simulation-id").val() > 0;
    $(".advanced-tab-extra-text").hide();
    $(".discard-changes").show();

    var modeTabsObj = $("#mode-tabs");
    modeTabsObj.find("a[href='#simple']").on("click", getUpdatedSummaryForm);
    modeTabsObj.find("a[href='#advanced']").on("click", function(e) {
        getUpdatedScenario(e, false, null, $("form").serializeArray(), $(this));
    });
});

function getUpdatedSummaryForm(e) {
    e.stopImmediatePropagation();

    var obj = $(this);
    var postVals = {'xml': window.xmleditor.getValue()};

    $.post("/ts_om/" + $("#scenario-id").val() + "/summary/update/form/", postVals, function(data) {
        if (data.hasOwnProperty("valid") && data.valid) {
            if (data.hasOwnProperty('name')) {
                $("#name").val(data["name"]);
            }

            obj.tab('show');
        }
    }, "json").fail(function(jqXHR, textStatus, errorThrown) {
    });
}

/**
 * Created by nreed on 10/30/14.
 */
$(function() {
  $("#list").addClass("active");

  $(".all-scenarios-checkbox").click(function() {
    var checked = $(this).prop("checked");
    $(".scenario-checkbox").each(function() {
      $(this).prop("checked", checked);
    });
  });

  $(".submit-scenarios").click(function() {
    var deleteMsg =  $("#delete-message");

    deleteMsg.hide();
    deleteMsg.empty();
    var ids = [];

    $(".scenario-checkbox").filter(":checked").each(function() {
      ids.push($(this).data("id"));
    });

    if (ids.length === 0) return;

    $.post("/ts_om/scenarios/submit/", { scenario_ids: JSON.stringify(ids) }, function (data) {
      if (data != null) {
        if (data.ok) {
          if (data.hasOwnProperty("scenarios")) {
            data.scenarios.forEach(function(scenario_data, index, array) {
              if (scenario_data.ok) {
                var scenario_row = $("#scenario-row-" + scenario_data.id);
                var simStatusObj = scenario_row.find(".sim-status");

                simStatusObj.html($(".sim-running-container").html());
              }
            });
          }
        }

        deleteMsg.removeClass("alert-error");
        deleteMsg.addClass("alert-success");
        deleteMsg.append("<p>Simulation(s) submitted.</p>");
        deleteMsg.show();
      } else {
        deleteMsg.removeClass("alert-success");
        deleteMsg.addClass("alert-error");
        deleteMsg.append("<p>Error submitting simulation(s).</p>");
        deleteMsg.show();
      }
    }, "json").fail(function(jqXHR, textStatus, errorThrown) {
      deleteMsg.append("<p>Error submitting simulation(s).</p>");
      deleteMsg.show();
    });
  });

  $(".delete").click(function() {
    var deleteMsg =  $("#delete-message");

    deleteMsg.hide();
    deleteMsg.empty();

    var ids = [];

    $(".scenario-checkbox").filter(":checked").each(function() {
     ids.push($(this).data("id"));
    });

    if (ids.length === 0) return;

    $.post("/ts_om/deleteScenario/", { scenario_ids: JSON.stringify(ids) }, function (data) {
      if (data != null) {
        if (data.ok) {
          ids.forEach(function(id, index, array) {
            var scenario_row = $("#scenario-row-" + id);
            var tooltip = scenario_row.find(".tooltip_button");

            scenario_row.animate({height: 0}, 1000, "linear", function () {
              tooltip.tooltip('hide');
              $(this).remove();
            });

            deleteMsg.removeClass("alert-error");
            deleteMsg.addClass("alert-success");
            deleteMsg.append("<p>Simulation(s) deleted.</p>");
            deleteMsg.show();
          });
        } else {
          deleteMsg.removeClass("alert-success");
          deleteMsg.addClass("alert-error");
          deleteMsg.append("<p>Error deleting simulation(s).</p>");
          deleteMsg.show();
        }
      }
    }, "json").fail(function(jqXHR, textStatus, errorThrown) {
      deleteMsg.append("<p>Error deleting simulation(s).</p>");
      deleteMsg.show();
    });
  });
});
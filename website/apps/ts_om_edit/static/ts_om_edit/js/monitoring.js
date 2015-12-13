/**
 * Created by nreed on 9/23/14.
 */
$(document).ready(function() {
  $("#monitoring").addClass("active");

  $("#id_parasite_detection_diagnostic_type").find("option[value='custom']").hide();

  if (measure_outputs == "yearly")
    $("#id_measure_outputs").find("option[value='custom']").hide();

  var modeTabsObj = $("#mode-tabs");
  modeTabsObj.find("a[href='#simple']").on("click", getUpdatedMonitoringForm);
  modeTabsObj.find("a[href='#advanced']").on("click", getUpdatedScenario);
});

function getUpdatedMonitoringForm(e) {
  e.stopImmediatePropagation();

  var surveyOptions = [
    "nr_per_age_group",
    "patent_infections",
    "uncomplicated_episodes",
    "severe_episodes",
    "hospitalizations",
    "direct_deaths",
    "indirect_deaths",
    "itn",
    "irs",
    "mda",
    "msat",
    "vaccine",
    "nr_infections"
  ];
  var obj = $(this);
  var postVals = {'xml': window.xmleditor.getValue(), 'start_date': $("#id_sim_start_date").val()};

  $.post("/ts_om/" + $("#scenario-id").val() + "/monitoring/update/form/", postVals, function(data) {
    if (data.hasOwnProperty("valid") && data.valid) {
      for (var i = 0; i < surveyOptions.length; i++) {
        if (data.hasOwnProperty(surveyOptions[i])) {
          $("#id_" + surveyOptions[i]).prop("checked", data[surveyOptions[i]]);
        }
      }

      $("#id_measure_outputs").val(data["measure_outputs"]);
      $("#id_monitor_start_date").val(data["monitor_start_date"]);
      $("#id_monitor_yrs").val(data["monitor_yrs"]);
      $("#id_monitor_mos").val(data["monitor_mos"]);
      $("#id_parasite_detection_diagnostic_type").val(data["parasite_detection_diagnostic_type"]);
      $("#surveys").val(data["surveys"]);

      obj.tab('show');
    }
  }, "json").fail(function(jqXHR, textStatus, errorThrown) {
  });
}
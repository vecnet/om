/**
 * Created by nreed on 10/30/14.
 */
$(function() {
  $("#healthsystem").addClass("active");

  var modeTabsObj = $("#mode-tabs");
  modeTabsObj.find("a[href='#simple']").on("click", getUpdatedHealthSystemForm);
  modeTabsObj.find("a[href='#advanced']").on("click", getUpdatedScenario);
});

function getUpdatedHealthSystemForm(e) {
  e.stopImmediatePropagation();

  var obj = $(this);
  var postVals = {'xml': window.xmleditor.getValue()};

  $.post("/ts_om/" + $("#scenario-id").val() + "/healthsystem/update/form/", postVals, function (data) {
    if (data.hasOwnProperty("valid") && data.valid) {
      $("#id_perc_total_treated").val(data["perc_total_treated"]);
      $("#id_perc_formal_care").val(data["perc_formal_care"]);
      $("#id_first_line_drug").val(data["first_line_drug"]);

      obj.tab('show');
    }
  }, "json").fail(function(jqXHR, textStatus, errorThrown) {
  });
}

/**
 * Created by nreed on 1/29/15.
 */
var MAX_XS_INT = 2147483647;

$(function () {
  var modeTabsObj = $("#mode-tabs");
  modeTabsObj.find("a[href='#simple']").on("click", getUpdatedInterventionsForm);
  modeTabsObj.find("a[href='#advanced']").on("click", getUpdatedScenario);

  var interventionsObj = $(".interventions");
  var uiSortableObj = $(".ui-sortable");

  $("#interventions").addClass("active");

  interventionsObj.on("click", ".ts-collapse", function () {
    var icon = $(this).find("i");
    var commonIconStr = "icon-chevron-";
    var upStr = commonIconStr + "up";
    var downStr = commonIconStr + "down";

    icon.hasClass(upStr) ? icon.removeClass(upStr).addClass(downStr) : icon.removeClass(downStr).addClass(upStr);
  });

  uiSortableObj.on("customLoadEvent", function() {
    $(".intervention:visible").each(function () {
      var prefix = $(this).data("prefix");
      var index = $(this).data("index");

      $(this).find(".intervention-vector-name:visible").each(function (innerIndex) {
        $(this).html($("#id_" + prefix + "-" + index + "-vector_" + innerIndex + "_mosquito").val());
      });

      $(this).find(".intervention-option-name:visible").each(function (innerIndex) {
        $(this).html($("#id_" + prefix + "-" + index + "-option_" + innerIndex + "_name").val());
      });
    });
  });

  uiSortableObj.trigger("customLoadEvent");
});

function getUpdatedInterventionsForm(e) {
  e.stopImmediatePropagation();

  var obj = $(this);
  var postVals = {'xml': window.xmleditor.getValue()};
  var uiSortableObj = $(".ui-sortable");

  uiSortableObj.empty();

  uiSortableObj.load("/ts_om/" + $("#scenario-id").val() + "/interventions/update/form/", postVals, function (data) {
    obj.tab('show');
    $(this).trigger("customLoadEvent");

    vectorsCount = parseInt($(".entomology-vectors-count").val());
    vectorNames = $(".entomology-vector-names").val();
  });
}

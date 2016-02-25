/**
 *
 * Created by nreed on 1/15/15.
 */
var monthlyValues = {};
var charts = [];
var options = {
  chart: {
    renderTo: 'chart',
    animation: false
  },
  title: {
    text: ''
  },
  xAxis: {
    title: {
      text: ''
    },
    categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  },
  yAxis: {
    min: 0,
    floor: 0,
    title: {
      text: 'Relative proportion of EIR per month'
    }
  },
  tooltip: {
    formatter: function () {
      var formattedY = (this.y === 0) ? 0 : this.y.toFixed(monthlyValues[this.series.name]['decimal_length']);

      return '<b>' + this.x + '</b><br/>Value: ' + formattedY;
    }
  },
  plotOptions: {
    series: {
      cursor: 'ns-resize',
      point: {
        events: {
          drag: function(e) {
            return true;
          },
          drop: function(e) {
            var obj = this;
            $(".vector").each(function(index) {
              if ($(this).find(".vector-name").html() == obj.series.name) {
                var moValDecLen = monthlyValues[obj.series.name]['decimal_length'];
                var num = (e.target.y === 0) ? 0 : parseFloat(e.target.y).toFixed(moValDecLen);
                var monthVals = monthlyValues[obj.series.name];

                monthVals[e.target.x] = parseFloat(num);
                monthlyValues[obj.series.name] = monthVals;
                $("#id_form-" + index + "-monthly_values").val(JSON.stringify(monthVals));

                return false;
              }
            });

            return true;
          }
        }
      },
      stickyTracking: false
    }
  },
  series: []
};

$(function() {
  $("#entomology").addClass("active");

  var modeTabsObj = $("#mode-tabs");
  modeTabsObj.find("a[href='#simple']").on("click", getUpdatedEntomologyForm);
  modeTabsObj.find("a[href='#advanced']").on("click", getUpdatedScenario);

  var vectorsObj = $(".vectors");

  vectorsObj.on("click", ".ts-collapse", function() {
    var icon = $(this).find("span");
    var commonIconStr = "glyphicon-chevron-";
    var upStr = commonIconStr + "up";
    var downStr = commonIconStr + "down";

    icon.hasClass(upStr) ? icon.removeClass(upStr).addClass(downStr) : icon.removeClass(downStr).addClass(upStr);
  });

  vectorsObj.on("click", ".remove-vector", function() {
    $("#modal-vector-mosquito").val($(this).data("id"));
  });

  var vectorSelObj = $("#id_vectors");
  vectorSelObj.change(function() {
    var obj = $(this);
    var vectorExists = false;

    $(".vector").each(function(index) {
      if ($(this).find(".vector-name").html() == $(obj).find("option:selected").data("name")
        && !$("#id_form-" + index + "-DELETE").prop("checked")) {
        vectorExists = true;
        return false;
      }
    });

    $(".add-vector").prop("disabled", vectorExists);
  });

  $("#remove").click(function () {
    var index = parseInt($("#modal-vector-mosquito").val());

    $(".vector:gt(" + index + ")").each(function(idx) {
      var newIndex = index + idx;
      var splitId = $(this).attr("id").split("_");
      $(this).attr("id", splitId[0] + "_" + newIndex);

        var $innerVector = $(this).find(".inner-vector");
        splitId = $innerVector.attr("id").split("_");
        $innerVector.attr("id", splitId[0] + "_" + newIndex);

        var $chart = $innerVector.find(".chart");
        splitId = $chart.attr("id").split("_");
        $chart.attr("id", splitId[0] + "_" + newIndex);

      var collapseObj = $(this).find(".ts-collapse");
      var splitTarget = collapseObj.data("target").split("_");
      collapseObj.attr("data-target", splitTarget[0] + "_" + newIndex);

      var removeBtn = $(this).find(".remove-vector");
      removeBtn.attr("data-id", newIndex);
      removeBtn.data("id", newIndex);

      $(this).find("label").each(function() {
        if ($(this).attr("for")) {
          updateFormElement($(this), "for", newIndex);
        }
      });

      $(this).find("input").each(function() {
        if ($(this).attr("id")) {
          updateFormElement($(this), "id", newIndex);
        }
        if ($(this).attr("name")) {
          updateFormElement($(this), "name", newIndex);
        }
      });

        charts[newIndex+1].options.chart.renderTo = "chart_" + newIndex;
    });

      charts.splice(index, 1);

    var obj = vectorsObj.find(".vector").get(index);
    $(obj).remove();

    $("#id_vectors").trigger("change");

    var totalFormsObj = $("#id_form-TOTAL_FORMS");
    var formCount = parseInt(totalFormsObj.val());

    if (formCount == 2) {
        var removeBtn = $(".vector").find(".remove-vector");
        removeBtn.prop("disabled", true);
        removeBtn.attr("title", "Must have at least one species in the simulation");
    }

    totalFormsObj.val(formCount-1);
  });

  $(".add-vector").click(function() {
    var totalFormsObj = $("#id_form-TOTAL_FORMS");
    var formCount = parseInt(totalFormsObj.val());
    $(".add-vector").prop("disabled", true);

    addVector(formCount);

    totalFormsObj.val(formCount + 1);

    if (formCount == 1) {
      var removeBtn = $(".vector:first").find(".remove-vector");

      removeBtn.prop("disabled", false);
      removeBtn.attr("data-type", "remove");
      removeBtn.attr("data-toggle", "modal");
      removeBtn.attr("data-target", "#confirm");
      removeBtn.attr("title", "Remove Vector and all related data");
    }
  });

  var vectorClassObj = $(".vector");
  var optionsList = [];

  vectorClassObj.each(function(index) {
    var vectorName = $("#id_form-" + index + "-name").val();

    $(this).find(".vector-name").html(vectorName);
    monthlyValues[vectorName] = JSON.parse($("#id_form-" + index + "-monthly_values").val());

    var moValStr = monthlyValues[vectorName][0].toString();
    monthlyValues[vectorName]['decimal_length'] = moValStr.split('.')[1].length;

    var seriesOptions = {
      name: vectorName,
      data: monthlyValues[vectorName],
      draggableY: true,
      dragMinY: 0
    };

    var newOptions = $.extend(true, {}, options);
    newOptions.chart.renderTo = "chart_" + index;
    newOptions.series.push(seriesOptions);
    optionsList.push(newOptions);
  });

    vectorClassObj.promise().done(function() {
        optionsList.forEach(function(item, index, array) {
            charts.push(new Highcharts.Chart(item));
        });
        $("#id_vectors").trigger("change");
    });

    $(".has-imported-infection").click(function() {
        $(".imported-infections").toggleClass("hide");
    });
});

function getUpdatedEntomologyForm(e) {
  e.stopImmediatePropagation();

  var obj = $(this);
  var postVals = {'xml': window.xmleditor.getValue()};

  $.post("/ts_om_edit/" + $("#scenario-id").val() + "/entomology/update/form/", postVals, function (data) {
    if (data.hasOwnProperty("valid") && data.valid) {
      $(".vectors").find(".vector").each(function() {
        $(this).remove();
      });

      //while (chart.series.length > 0) chart.series[0].remove();
        while (charts.length > 0) charts.pop();

      var hasInterventions = data["has_interventions"];

      if (data.hasOwnProperty("vectors")) {
        $.each(data.vectors, function (index, value) {
          addVector(index, value, hasInterventions);
        });
        $("#id_form-TOTAL_FORMS").val(data.vectors.length);
      }
      $("#id_vectors").trigger("change");
      obj.tab('show');

        $(".has-imported-infection").prop("checked", data["has_imported_infection"]);
        $(".imported-infections").toggleClass("hide", !data["has_imported_infection"]);

        if (data["has_imported_infection"]) {
            var importedInfection = data["imported_infection"];

            $("input[name='period']").val(importedInfection["period"]);
            $("input[name='name']").val(importedInfection["name"]);
            $("input[name='timesteps']").val(importedInfection["timesteps"]);
            $("input[name='values']").val(importedInfection["values"]);
        }
    }
  }, "json").fail(function(jqXHR, textStatus, errorThrown) {
  });
}

function updateFormElement(elem, attr, nr) {
  var split = elem.attr(attr).split('-');
  var newStr = split[0] + '-' + nr + '-' + split[2];

  elem.attr(attr, newStr);
}

function addVector(count, vector, hasInterventions) {
  hasInterventions = hasInterventions || false;
  var obj = $(".hidden-vector").clone().get(0);

  $(obj).removeClass("hidden-vector hide").addClass("vector");
  $(obj).attr('id', 'vector_' + count).hide().appendTo(".vectors").slideDown(300);
  $(obj).find(".ts-collapse").attr("data-target", "#inner-vector_" + count);
  $(obj).find(".inner-vector").attr("id", "inner-vector_" + count);

  var removeBtn = $(obj).find(".remove-vector");
  if (hasInterventions) {
    removeBtn.prop("disabled", true);
    removeBtn.attr("title", "Can't change species list if intervention section is not empty");
  } else {
    removeBtn.attr("data-id", count);
  }

  $(obj).find("label").each(function () {
    if ($(this).attr("for")) {
      updateFormElement($(this), "for", count);
    }
  });

  $(obj).find("input").each(function () {
    if ($(this).attr("id")) {
      updateFormElement($(this), "id", count);
    }
    if ($(this).attr("name")) {
      updateFormElement($(this), "name", count);
    }
  });

  var name = "";
  var avgEir = 0;
  var bloodIdx = 0;
  var monthlyVals = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];

  if (vector != null) {
    name = vector.name;
    avgEir = vector["average_eir"];
    bloodIdx = vector["human_blood_index"];
    monthlyVals = vector["monthly_values"];
  } else {
    var selectedVectorObj = $("#id_vectors").find("option:selected");
    name = selectedVectorObj.data("name");
    avgEir = selectedVectorObj.data("averageEir") * 100;
    bloodIdx = selectedVectorObj.data("humanBloodIndex") * 100;
    monthlyVals = selectedVectorObj.data("monthlyValues");
  }

  $("#id_form-" + count + "-name").val(name);
  $("#id_form-" + count + "-average_eir").val(avgEir);
  $("#id_form-" + count + "-human_blood_index").val(bloodIdx);
  $("#id_form-" + count + "-monthly_values").val(JSON.stringify(monthlyVals));
  $(obj).find(".vector-name").html(name);

  monthlyValues[name] = monthlyVals;
  var moValStr = monthlyValues[name][0].toString();
  var moStrSplt = moValStr.split('.');

  monthlyValues[name]['decimal_length'] = (moStrSplt.length > 1) ? moStrSplt[1].length : 0;

  var seriesOptions = {
    name: name,
    data: monthlyVals,
    draggableY: true,
    dragMinY: 0
  };

    $(obj).find(".chart").attr("id", "chart_" + count);

    var newOptions = $.extend(true, {}, options);
    newOptions.chart.renderTo = "chart_" + count;
    newOptions.series.push(seriesOptions);
    charts.push(new Highcharts.Chart(newOptions));
}

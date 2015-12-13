/**
 * Created by nreed on 5/13/15.
 */
var vectorsCount = 0;
var vectorNames = [];

$(function() {
  var cartDiv = $(".cart");
  var interventionDiv = $("#intervention");

  interventionDiv.find("ul li").draggable({
    connectToSortable: ".cart",
    helper: "clone",

    drag: function (e) {
      if ($(this).attr("class").match(/disabled/g)) {
        e.preventDefault();
        return;
      }

      $(this).addClass("active");
      $(this).closest("#intervention").addClass("active");
    },

    stop: function () {
      $(this).removeClass("active").closest("#intervention").removeClass("active");
    }
  });

  cartDiv.sortable({
    tolerance:"touch",

    over: function () {
      $(this).addClass("hover");
    },

    out: function () {
      $(this).removeClass("hover");
    },

    update: function (event, ui) {
      if (ui.item.attr("class").match(/ui-draggable/g)) {
        var uiItem = $(ui.item);
        var selectedName = uiItem.data("name");
        var prefix = uiItem.data("prefix");

        addIntervention(prefix, selectedName, ui.item[0]);
      }
    }
  });

  interventionDiv.find("ul li").find(".add-button").click(function () {
    if ($(this).not('.ui-draggable-dragging')) {
      var selectedInterventionObj = $(this).parents(".ui-draggable");

      addIntervention(selectedInterventionObj.data("prefix"), selectedInterventionObj.data("name"));

      return false;
    }
  });

  cartDiv.on("click", "li button.delete-entry", function () {
    $('.tooltip').remove();
    var listItem = $(this).closest("li");
    var prefix = listItem.data("prefix");

    removeIntervention(prefix, listItem.data("index"));

    var totalFormObj = $("#id_" + prefix + "-TOTAL_FORMS");
    var totalFormCount = parseInt(totalFormObj.val());

    totalFormObj.val(--totalFormCount);

    listItem.remove();
  });

  if ($(".interventions").find(".intervention:visible").filter(function () {
    return $(this).data("prefix") === "importedinfections";
  }).length > 0) {
    interventionDiv.find(".ui-draggable").filter(function() {
      return $(this).data("prefix") === "importedinfections";
    }).each(function () {
      $(this).addClass("disabled");

      var buttonObj = $(this).find(".add-button");

      buttonObj.attr("disabled", "disabled");
      buttonObj.addClass("disabled");
    });
  }
});

function updateFormElement(elem, attr, splitStr, nr) {
  var split = elem.attr(attr).split(splitStr);
  var newStr = split[0] + nr + split[1];

  elem.attr(attr, newStr);
}

function addIntervention(prefix, selectedName, uiObj) {
  var name = selectedName;

  if (prefix === "pev" || prefix === "bsv" || prefix === "tbv") {
    prefix = "vaccine";
  } else if (prefix === "importedinfections") {
    $(".ui-draggable").filter(function() {
      return $(this).data("prefix") === prefix;
    }).each(function () {
      $(this).addClass("disabled");

      var buttonObj = $(this).find(".add-button");

      buttonObj.attr("disabled", "disabled");
      buttonObj.addClass("disabled");
    });
  }

  var newFormObj = $($("#empty-form-" + prefix).clone(false).get(0));

  $(".interventions").find(".intervention:visible").filter(function () {
    return $(this).data("prefix") === prefix; // && $(this).data("empty") === "";
  }).each(function (index) {
    var divPrefix = "#id_" + prefix + "-" + index + "-";
    var uniqueInterventionName = $(divPrefix + "id").length ? $(divPrefix + "id").val() : $(divPrefix + "name").val();
    if (uniqueInterventionName === name) {
      var addedCt = 0;
      var newIdFound = false;

      do {
        newIdFound = true;
        addedCt++;
        name = selectedName + "-" + addedCt;

        $(".intervention:visible").filter(function () {
          return $(this).data("prefix") === prefix; // && $(this).data("empty") === "";
        }).each(function (innerIndex) {
          var divPrefix = "#id_" + prefix + "-" + innerIndex + "-";
          var uniqueInterventionName = $(divPrefix + "id").length ? $(divPrefix + "id").val() : $(divPrefix + "name").val();
          if (uniqueInterventionName === name) {
            newIdFound = false;
            return newIdFound;
          }
        });
      } while (!newIdFound);

      return false;
    }
  });

  var totalFormObj = $("#id_" + prefix + "-TOTAL_FORMS");
  var totalFormCount = parseInt(totalFormObj.val());

  newFormObj.find("label").each(function () {
    if ($(this).attr("for")) {
      updateFormElement($(this), "for", "__prefix__", totalFormCount);
    }
  });

  newFormObj.find("input").each(function () {
    if ($(this).attr("id")) {
      updateFormElement($(this), "id", "__prefix__", totalFormCount);
    }
    if ($(this).attr("name")) {
      updateFormElement($(this), "name", "__prefix__", totalFormCount);
    }
  });

  var divPrefix = prefix + "-" + totalFormCount;
  var uniqueDivPrefix = "#id_" + divPrefix  + "-";
  var uniqueNameHiddenDiv = newFormObj.find(uniqueDivPrefix + "id");

  if (!uniqueNameHiddenDiv.length) {
    uniqueNameHiddenDiv = newFormObj.find(uniqueDivPrefix + "name");
    selectedName = name;
  } else {
    newFormObj.find(uniqueDivPrefix + "name").val(selectedName);
  }

  uniqueNameHiddenDiv.val(name);
  newFormObj.find(".intervention-id-inner").text(name);
  newFormObj.find(".intervention-name").text(selectedName);
  newFormObj.find(".edit-intervention").attr("data-target", "#intervention-" + divPrefix);
  newFormObj.find(".intervention-details").attr("id", "intervention-" + divPrefix);
  newFormObj.find(".intervention").attr("data-empty", "");
  newFormObj.find(".intervention").data("empty", "");
  newFormObj.find(".intervention").attr("data-index", totalFormCount);
  newFormObj.find(".intervention").data("index", totalFormCount);

  if (prefix == "gvi" || prefix == "intervention") {
    var emptyVectorObj = newFormObj.find(".intervention").find(".intervention-details").find(".empty-vector");

    for (var i = 0; i < vectorsCount; i++) {
      var newVectorObj = $(emptyVectorObj.clone(false).get(0));

      newVectorObj.find("label").each(function () {
        if ($(this).attr("for")) {
          updateFormElement($(this), "for", "__inner-prefix__", i);
        }
      });

      newVectorObj.find("input").each(function () {
        if ($(this).attr("id")) {
          updateFormElement($(this), "id", "__inner-prefix__", i);
        }
        if ($(this).attr("name")) {
          updateFormElement($(this), "name", "__inner-prefix__", i);
        }
      });

      var newMosquitoObj = $($("#id_" + prefix + "-__prefix__-vector___inner-prefix___mosquito").clone(false).get(0));

      updateFormElement(newMosquitoObj, "id", "__prefix__", totalFormCount);
      updateFormElement(newMosquitoObj, "name", "__prefix__", totalFormCount);
      updateFormElement(newMosquitoObj, "id", "__inner-prefix__", i);
      updateFormElement(newMosquitoObj, "name", "__inner-prefix__", i);

      newVectorObj.find(".intervention-vector-name").html(vectorNames[i]);
      newMosquitoObj.val(vectorNames[i]);

      var newInterventionDetailsObj = newFormObj.find(".intervention").find(".intervention-details");
      newInterventionDetailsObj.append(newVectorObj.html());
      newInterventionDetailsObj.append(newMosquitoObj);
    }
  }

  if (uiObj) {
    uiObj.outerHTML = newFormObj.html();
  } else {
    var newInterventionObj = $(".intervention:visible:last");

    if (newInterventionObj.length > 0) {
      newInterventionObj.after(newFormObj.html());
    } else {
      $(".cart").append(newFormObj.html());
    }
  }

  totalFormObj.val(++totalFormCount);
}

function removeIntervention(prefix, index) {
  $(".interventions").find(".intervention:visible").filter(function() {
    return $(this).data("prefix") === prefix /* && $(this).data("empty") === "" */ && $(this).data("index") > index;
  }).each(function(innerIndex) {
    var oldIndex = $(this).data("index");
    var newIndex = index + innerIndex;
    var prefixStr = prefix + "-";

    $(this).find("label").each(function () {
      if ($(this).attr("for")) {
        updateFormElement($(this), "for", prefixStr + oldIndex, prefixStr + newIndex);
      }
    });

    $(this).find("input").each(function () {
      if ($(this).attr("id")) {
        updateFormElement($(this), "id", prefixStr + oldIndex, prefixStr + newIndex);
      }
      if ($(this).attr("name")) {
        updateFormElement($(this), "name", prefixStr + oldIndex, prefixStr + newIndex);
      }
    });

    $(this).find(".edit-intervention").attr("data-target", "#intervention-" + prefix + "-" + newIndex);
    $(this).find(".intervention-details").attr("id", "intervention-" + prefix + "-" + newIndex);
    $(this).attr("data-index", newIndex);
    $(this).data("index", newIndex);
  });

  if (prefix == "importedinfections") {
    $(".ui-draggable").filter(function() {
      return $(this).data("prefix") === prefix;
    }).each(function () {
      $(this).removeClass("disabled");

      var buttonObj = $(this).find(".add-button");

      buttonObj.removeAttr("disabled");
      buttonObj.removeClass("disabled");
    });
  }
}

var tags = {};
var xmlChanged = false;
var scenarioId = -1;

$(document).ready(function () {
    $.getJSON(STATIC_URL_XML_TAGS, function (data) {
        tags = data;
    });

    scenarioId = parseInt($("#scenario-id").val());

    $('a[data-toggle="tab"]').on("shown.bs.tab", function(e) {
        if ($(this).attr("href") == "#advanced") {
            refreshXmlEditor();
            window.xmleditor.mirror.execCommand("goDocStart");
        }
    });

    $("#validate").click(function() {
        validate();
    });


    var hasSim = $("#simulation-id").val() > 0;
    var textarea = document.getElementById("xml");
    var uiOptions =  {
        path: 'js/',
        searchMode: 'popup',
        imagePath: CODEMIRROR_IMG_PATH,
        buttons: ['search', 'undo', 'redo', 'jump', 'reindent', 'about'],
        saveCallback: function() {}
    };
    var codeMirrorOptions = {
        mode: "xml",
        matchBrackets: true,
        autoCloseTags: {
            whenClosing: true,
            whenOpening: true,
            dontCloseTags: [""],
            indentTags: indentTags
        },
        lineNumbers: true,
        indentUnit: 4,
        extraKeys: {
            "'<'": completeAfter,
            "'/'": completeIfAfterLt,
            "' '": completeIfInTag,
            "'='": completeIfInTag,
            "Ctrl-Space": function (cm) {
                CodeMirror.showHint(cm, CodeMirror.hint.xml, {schemaInfo: tags});
            },
            "F11": function(cm) {
                cm.setOption("fullScreen", !cm.getOption("fullScreen"));
            },
            "Esc": function(cm) {
                if(cm.getOption("fullScreen")) cm.setOption("fullScreen", false);
            },
            "Ctrl-J": "toMatchingTag",
            "Shift-Tab": autoFormatSelection,
            "Ctrl-K": commentSelection
        },
        lineWrapping: true,
        autofocus: true,
        foldGutter: true,
        gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter", "CodeMirror-lint-markers"],
        matchTags: {bothTags: true},
        styleSelectedText: true,
        readOnly: hasSim
    };

    CodeMirrorUI.prototype.reindent = autoFormatDocument; // Override.

    var editor = new CodeMirrorUI(textarea, uiOptions, codeMirrorOptions);

    editor.removeClass(editor.undoButton, 'inactive');
    editor.removeClass(editor.redoButton, 'inactive');

    window.xmleditor = editor;

    if (hasSim) {
      $(".advanced-tab-extra-text").show();
    }
});

function completeAfter(cm, pred) {
    if (!pred || pred()) setTimeout(function() {
        if (!cm.state.completionActive)
            CodeMirror.showHint(cm, CodeMirror.hint.xml, {schemaInfo: tags, completeSingle: false});
    }, 100);
    return CodeMirror.Pass;
}

function completeIfAfterLt(cm) {
    return completeAfter(cm, function() {
        var cur = cm.getCursor();
        return cm.getRange(CodeMirror.Pos(cur.line, cur.ch - 1), cur) == "<";
    });
}

function completeIfInTag(cm) {
    return completeAfter(cm, function() {
        var tok = cm.getTokenAt(cm.getCursor());
        if (tok.type == "string" && (!/['"]/.test(tok.string.charAt(tok.string.length - 1)) || tok.string.length == 1)) return false;
        var inner = CodeMirror.innerMode(cm.getMode(), tok.state).state;
        return inner.tagName;
    });
}

function undo() {
    window.xmleditor.undo()
}
function redo() {
    window.xmleditor.redo()
}

function getSelectedRange() {
    return { from: window.xmleditor.mirror.getCursor(true), to: window.xmleditor.mirror.getCursor(false) };
}

function autoFormatSelection() {
    var range = getSelectedRange();
    window.xmleditor.mirror.autoFormatRange(range.from, range.to);
}

function autoFormatDocument() {
    window.xmleditor.mirror.autoFormatRange({line:0, ch:0}, {line:window.xmleditor.mirror.lineCount()});
}

function commentSelection() {
    var range = getSelectedRange();
    window.xmleditor.mirror.commentRange(true, range.from, range.to);
}

function refreshXmlEditor() {
    if (xmlChanged) {
        autoFormatDocument();
        xmlChanged = false;
    }
}

function getXmlObjectFromString(xmlStr) {
    var xmlDoc = "";

    try {
        xmlDoc = $.parseXML(xmlStr);
    } catch (e) {
        return e;
    }

    return $(xmlDoc);
}

function getScenarioXml() {
    var xml = window.xmleditor.getValue();
    var xmlDoc = "";

    try {
        xmlDoc = $.parseXML(xml);
    } catch (e) {
        return e;
    }

    return $(xmlDoc);
}

function updateEditorXml(xml) {
    var xmlObj = xml.get(0);
    var xmlSerializer = new XMLSerializer();
    var xmlStr = xmlSerializer.serializeToString(xmlObj);

    window.xmleditor.mirror.replaceRange(xmlStr, {line: 0, ch: 0}, {line: window.xmleditor.mirror.lineCount()});
    xmlChanged = true;
}

function validate(callback) {
    var valid = false;
    var validateSpinner = $("#validate-spinner");
    var validOrNo = $("#valid-or-not");

    validateSpinner.show();
    validOrNo.hide();
    validOrNo.empty();

    var xml = window.xmleditor.getValue();
    var xmlDoc = "";

    try {
        xmlDoc = $.parseXML(xml);
    } catch (e) {
        validOrNo.removeClass("alert alert-success");
        validOrNo.addClass("alert alert-error");
        validOrNo.show();
        validOrNo.append("<p>Invalid XML</p><p>Parser error<p>");
        validateSpinner.hide();

        if (typeof(callback) === "function")
            return callback(false);

        return;
    }

    $xml = $(xmlDoc);
    $scenario = $xml.find("om\\:scenario");

    if ($scenario != null) {
        schemaFileStr = $scenario.attr("xsi:schemaLocation");

        if (schemaFileStr != null && schemaFileStr.indexOf("current") > -1) {
            validOrNo.removeClass("alert alert-success");
            validOrNo.addClass("alert alert-error");
            validOrNo.show();
            validOrNo.append("<p>Invalid</p>" +
                "<p>Wrong schema file specified." +
                " Please change scenario_<strong>current</strong>.xsd to scenario_<strong>32</strong>.xsd<p>" +
                "<p>in 'xsi:schemaLocation' attribute of root node 'om:scenario'.<p>");

            validateSpinner.hide();

            if (typeof(callback) === "function")
                return callback(false);

            return;
        }
    }

    $.post("/ts_om/restValidate/", xml, function(data) {
       if (data != null && data != "") {
           valid = data.result == 0;
           var validStr = valid ? "Valid" : "Invalid";

           if (valid) {
                validOrNo.removeClass("alert alert-error");
                validOrNo.addClass("alert alert-success");
           } else {
                validOrNo.removeClass("alert alert-success");
                validOrNo.addClass("alert alert-error");
           }

           validOrNo.show();
           validOrNo.append("<p>" + validStr + "</p>");

           if (data.result != 0) {
               for (var i = 0; i < data.om_output.length; i++) {
                   validOrNo.append("<p>" + data.om_output[i] + "</p>");
               }
           }

           if (typeof(callback) === "function")
               callback(valid);
       }

       validateSpinner.hide();

       if (typeof(callback) === "function")
           callback(valid);
    }, "json").fail(function(jqXHR, textStatus, errorThrown) {
       validateSpinner.hide();

       if (typeof(callback) === "function")
           callback(valid);
    });
}

function saveScenario(callback) {
    var xml = window.xmleditor.getValue();
    var valid = false;

    if (scenarioId > -1) {
        $.post("/ts_om/update/", {scenario_id:scenarioId, xml:xml}, function (data) {
            valid = false;
            if (data.hasOwnProperty("status")) {
                if (data.status == "ok"){valid=true}
            }
            if (typeof(callback) === "function")
                callback(valid);
        }, "json").fail(function(jqXHR, textStatus, errorThrown) {
            if (typeof(callback) === "function")
                callback(false);
        });
    }
}

function getUpdatedScenario(e, save, callback, data, obj) {
  save = save || false;
  e.stopImmediatePropagation();

  obj = obj || $(this);
  var updated = false;

    data = data || [];

    data = data.concat($("#ts-om-form").serializeArray());

  data.push({name: 'xml', value: window.xmleditor.getValue()});
  data.push({name: 'save', value: save});

  $.post(window.location.href, data, function(data) {
    if (data.hasOwnProperty("xml")) {
      var xml = data.xml;

      if (xml != null) {
        var xmlObj = getXmlObjectFromString(xml);

        if (xmlObj != null) {
          updateEditorXml(xmlObj);
          updated = true;
        }
      }
    }

    if (updated) {
      obj.tab('show');
    }

    if (callback != null) {
      callback();
    }
  }, "json").fail(function(jqXHR, textStatus, errorThrown) {
  });
}

var indentTags =
[
    "slope",
    "femaleEggsLaidByOviposit",
    "ripRate",
    "subPop",
    "uncomplicatedCaseDuration",
    "human",
    "developmentDuration",
    "changeHS",
    "decisions",
    "NonMalariaFevers",
    "group",
    "parameters",
    "decay",
    "treatment",
    "timedBase",
    "effectNegativeTest",
    "effectNeed",
    "initialACR",
    "ripFactor",
    "IC50",
    "pharmacology",
    "entomology",
    "deploymentBase",
    "BetaMeanSample",
    "TreatmentEfficacy",
    "effects",
    "deployment",
    "changeEIR",
    "IRSDescription",
    "probDeathOvipositing",
    "mosqProbOvipositing",
    "item",
    "demography",
    "initialInsecticide",
    "initialEfficacy",
    "treatmentActions",
    "SP",
    "cumulativeCoverage",
    "weight",
    "pSequelaeInpatient",
    "pupalStage",
    "SPAQ",
    "mosqProbResting",
    "rate",
    "ModelOptions",
    "emergenceReduction",
    "nonVector",
    "pEventIsSevere",
    "insertR_0Case",
    "healthSystem",
    "attritionOfNets",
    "decision",
    "schedule",
    "intervention",
    "complicatedRiskDuration",
    "HSEventScheduler",
    "SurveyOptions",
    "PD",
    "effectPositiveTest",
    "PK",
    "availabilityToMosquitoes",
    "lifeCycle",
    "importedInfections",
    "cohorts",
    "DecayFunction",
    "max_killing_rate",
    "om:scenario",
    "insecticideDecay",
    "component",
    "diagnostic",
    "half_life",
    "mosqProbFindRestSite",
    "complicated",
    "eggStage",
    "effectivenessOnUse",
    "prNeedTreatmentMF",
    "bloodStageLengthDays",
    "prTreatment",
    "selfTreatment",
    "vaccineDescription",
    "compliance",
    "drug",
    "holeRate",
    "negligible_concentration",
    "LognormalSample",
    "timed",
    "mosq",
    "timedDeployment",
    "Screen",
    "availabilityVariance",
    "pUseUncomplicated",
    "primaquine",
    "massListWithCum",
    "seasonality",
    "pEventSecondary",
    "ITNDeterrency",
    "nonHumanHosts",
    "ACT",
    "pEventPrimary",
    "TreatmentOption",
    "efficacyB",
    "surveys",
    "restrictToSubPop",
    "positive",
    "HSDiagnostic",
    "negative",
    "mosqLaidEggsSameDayProportion",
    "clinical",
    "pSelfTreatUncomplicated",
    "preprandialKillingEffect",
    "HSESTreatmentModifierEffect",
    "vectorPop",
    "bloodStageProtectionLatency",
    "TriggeredDeployments",
    "vol_dist",
    "EIRDaily",
    "option",
    "dailyPrImmUCTS",
    "continuous",
    "ITNDescription",
    "mosqProbBiting",
    "vivax",
    "intValue",
    "allele",
    "CQ",
    "GVIDescription",
    "complicatedCaseDuration",
    "HumanInterventionComponent",
    "developmentSurvival",
    "nonCompliersEffective",
    "initial_frequency",
    "medicate",
    "mosqSeekingDuration",
    "hypnozoiteReleaseDelayDays",
    "modifier",
    "ageGroup",
    "NormalSample",
    "mosqHumanBloodIndex",
    "mosqSurvivalFeedingCycleProbability",
    "interventions",
    "HSImmediateOutcomes",
    "subPopRemoval",
    "pSeekOfficialCareUncomplicated2",
    "pSeekOfficialCareUncomplicated1",
    "mosqRelativeEntoAvailability",
    "larvalStage",
    "uninfectVectors",
    "postprandialKillingEffect",
    "pHumanCannotReceive",
    "monitoring",
    "probBloodStageInfectiousToMosq",
    "Component",
    "anopheles",
    "maxUCSeekingMemory",
    "prNeedTreatmentNMF",
    "parameter",
    "anophelesParams",
    "MDAComponent",
    "ITNKillingEffect",
    "usage",
    "description",
    "deploy",
    "incidence",
    "drugRegimen",
    "treatments",
    "surveyTime",
    "AQ",
    "pSeekOfficialCareSevere",
    "ClinicalOutcomes",
    "extrinsicIncubationPeriod",
    "doubleList",
    "simpleMPD",
    "numberHypnozoites",
    "uncomplicated",
    "mass",
    "seekingDeathRateIncrease",
    "mosqRestDuration",
    "model",
    "deterrency",
    "CFR",
    "effectInformal",
    "QN"
];


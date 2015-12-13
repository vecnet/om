/**
 * Created by nreed on 10/22/14.
 */
var age_xml_list = {};

$(function() {
    $("#demography").addClass("active");

    $(".age_dist_xml").each(function () {
       age_dist_dict = {
         'name': $(this).data("name"),
         'title': $(this).data("title"),
         'xml': $.parseXML($(this).data("xml")),
         'url': $(this).data("url"),
         'maximumAgeYrs': $(this).data("maximumAgeYrs")
       };
       age_xml_list[$(this).attr('id')] = age_dist_dict;
    });

    var options = {
        chart: {
            renderTo: 'chart',
            type: 'column'
        },
        title: {
            text: 'Age Distribution'
        },
        xAxis: {
            title: {
                text: 'Age - Upperbound'
            },
            categories: []
        },
        yAxis: {
            title: {
                text: 'Percentage of Population'
            }
        },
        series: []
    };

    $("#id_age_dist").change(function () {
        options.series = [];
        var pop_percent_data = [];
        var age_dist_name = $(this).val();
        var age_dist = age_xml_list[age_dist_name];
        var $xml = $(age_dist['xml']);
        var age_dist_url = $("#age-dist-url");

        var xmlObj = $(age_dist['xml']).get(0);
        var xmlSerializer = new XMLSerializer();
        var xmlStr = xmlSerializer.serializeToString(xmlObj);

        var ageDistNameStr = age_dist_name == "custom" ? age_dist["name"] : age_dist_name;
        $("#id_age_dist_name").val(ageDistNameStr);
        $("#id_age_dist_xml").val(xmlStr);
        $("#id_maximum_age_yrs").val(age_dist['maximumAgeYrs']);

        if ($(this).val() != "custom")
            age_dist_url.show();
        else
            age_dist_url.hide();

        age_dist_url[0].href = age_dist['url'];

        $xml.find("group").each(function() {
            options.xAxis.categories.push($(this).attr("upperbound"));
            pop_percent_data.push(parseFloat($(this).attr("poppercent")));
        });

        seriesOptions = {
            name: age_dist_name,
            data: pop_percent_data
        };

        options.series.push(seriesOptions);

        var chart = new Highcharts.Chart(options);
    }).trigger('change');

  var modeTabsObj = $("#mode-tabs");
  modeTabsObj.find("a[href='#simple']").on("click", getUpdatedDemographyForm);
  modeTabsObj.find("a[href='#advanced']").on("click", getUpdatedScenario);
});

function getUpdatedDemographyForm(e) {
  e.stopImmediatePropagation();

  var obj = $(this);
  var postVals = {'xml': window.xmleditor.getValue()};

  $.post("/ts_om/" + $("#scenario-id").val() + "/demography/update/form/", postVals, function(data) {
    if (data.hasOwnProperty("valid") && data.valid) {
      var ageDistObj = $("#id_age_dist");

      $("#id_human_pop_size").val(data["human_pop_size"]);

      if (data.hasOwnProperty('title')) {
        ageDistInfo = {
          'name': data.name,
          'title': data.title,
          'xml': $.parseXML(data.xml),
          'url': '',
          'maximumAgeYrs': data['maximum_age_yrs']
        };
        age_xml_list['custom'] = ageDistInfo;

        ageDistObj.children("option").filter(":selected").prop("selected", false);
        ageDistObj.val('custom');

        var customObj = ageDistObj.children("option").filter(":selected");
        customObj.text('Custom (' + data.title + ')');
        customObj.show();
      } else {
        ageDistObj.val(data["age_dist"]);
      }

      obj.tab('show');
      ageDistObj.trigger('change');
    }
  }, "json").fail(function(jqXHR, textStatus, errorThrown) {
  });
}

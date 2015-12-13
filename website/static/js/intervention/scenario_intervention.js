///////////////////////////////////////////////////////////////////////////////
// VECNet CI - Prototype
// Date: 4/5/2013
// Institutions:
//      University of Notre Dame
//      Pittsburgh Supercomputing Center - Carnegie Mellon University
// Authors:
//      Robert Jones <Robert.Jones.428@nd.edu>
//      Jay DePasse <depasse@psc.edu>
//
// Dependencies:
//      sprintf.js (https://github.com/alexei/sprintf.js)
///////////////////////////////////////////////////////////////////////////////

// unique ID for selected Intervention rows' settings validation
var idCounter = new Date().getTime();

// Method to be executed when page has been loaded 
$(function () {

    $(".dropdown-menu li a").click(function(){
    
        filt_int_class = $(this).attr('id')
        console.log(filt_int_class);
        if (filt_int_class == 'AllInterventions') {
            $('ul li.filterable_intervention').show();
        }
        else {
            $('ul li.filterable_intervention').not(filt_int_class).hide();
            $('ul li.'+filt_int_class).show();
        }
    });

    // jQuery UI Draggable
    $("#intervention ul li").draggable({
        connectToSortable: ".cart",
        // clone available intervention entry so users can reuse.
        helper:"clone",
        // brings the item back to its place when dragging is over
        //revert:true,

        // once the dragging starts, we decrease the opactiy of other items
        // Appending a class as we do that with CSS
        drag:function () {
            $(this).addClass("active");
            $(this).closest("#intervention").addClass("active");
        },

        // removing the CSS classes once dragging is over.
        stop:function () {
            $(this).removeClass("active").closest("#intervention").removeClass("active");
        }
    });

    // jQuery Ui Droppable
    $(".cart").sortable({

        // The sensitivity of acceptance of the item once it touches the
        // to-be-dropped-element cart
        tolerance:"touch",

        // The class that will be appended once we are hovering the
        // to-be-dropped-element (cart)
        // hoverClass :"hover",  hoverClass works for droppable but not sortable
        over:function () {
            $(this).addClass("hover");
            //$(this).closest("#intervention").addClass("active");
        },

        // Remove the class when hovering stops
        out:function () {
            $(this).removeClass("hover");
            //$(this).closest("#intervention").addClass("active");
        },

        // This function runs when an item is dropped in the cart
        // change the dragged item to match the format for inputting the fields.
        // this would be better done in receive:(), but doesn't work there, see
        // jQuery bug #4303
        update:function (event, ui) {
            if ( ui.item.attr("class").match(/ui-draggable/g)) {
                var liID = ui.item.attr("data-id");
                var liName = ui.item.attr("data-name");
                var liSupportedModelsCSV = ui.item.attr("data-supported_models_csv");
                ui.item[0].outerHTML = li_get(liID, liName, 0, 1, -1, 100, 1,
                        liSupportedModelsCSV);
                $('.btn-small').tooltip({container:'body', placement:'top'});
            }
        }
    });


    // This function runs when "add" button is clicked (add to cart)
    $("#intervention ul li button.add_button").click(function (mouseEvent) {
        if ( $(this).not('.ui-draggable-dragging') ) {
            var liID = $(this).closest('li').attr('data-id');
            var liName = $(this).closest('li').attr('data-name');
            var liSupportedModelsCSV = $(this).closest('li').attr(
                'data-supported_models_csv');
            li_append(liID, liName, 0, 1, -1, 100, 1, liSupportedModelsCSV);
            return false;
        }
    });

    // This function runs when "duplicate" button is clicked (duplicate
    // existing intervention and then add to library)
    $("#intervention ul li button.duplicate_button").click(function (mouseEvent) {
        if ( $(this).not('.ui-draggable-dragging') ) {
            var modal_data_target = $(this).attr('data-modal_data_target');
            var liInterventionDefinition = $.parseJSON(
                $(this).closest('li').attr('data-intervention_definition'));
            // for right now, collect the existing options, modify, then
            // use to create new widget... eventually all common options
            // should be stored separately for reuse, or each individual
            // intervention can provide its own options.
            options = $("#xml_editor").data("xmlEditor").options;
            // TODO support the case where multiple specific-model interventions
            // TODO must be edited in sequence.  Right now assume that there's
            // TODO only one....
            for (var k in liInterventionDefinition) {
                options['xml_input_string'] = liInterventionDefinition[k];
                break;
            }
            $("#xml_editor").xmlEditor(options);
            $(modal_data_target).modal('show');
            return false;
        }
    });

    // This function runs when delete button is pressed
    $(".cart li button.delete").live("click", function () {
        $('.tooltip').remove();  //remove the tool tip element
        $(this).closest("li").remove();
    });

    // This function loads the cart with previously selected interventions
    // (from step storage - collected in view)
    if (this.intervention_selected != undefined
            && this.intervention_selected != null
            && this.intervention_selected != "[]"
            && this.intervention_selected != "") {

        // string substitution moved into function paramStringToArray (r2765)
        intervention_array = paramStringToArray(intervention_selected);
        start_day = paramStringToArray(start_day);
        num_reps = paramStringToArray(num_reps);
        days_between = paramStringToArray(days_between);
        demographic_coverage = paramStringToArray(demographic_coverage);
        //efficacy = paramStringToArray(efficacy);

        for (var i=0; i < intervention_array.length; i++) {
            intervention = intervention_array[i].split(":");
            var liID = intervention[0].replace (/ /g, '');
            // Don't display the intervention if no ID
            if ( liID > 0 || liID.match(/template/) || liID.match(/run/)) {
                var liName = intervention[1];
                var liStart_day = start_day[i]  || 0;
                var liNum_rep = num_reps[i] || 1; // actually num_distributions!
                var liDays_between = days_between[i] || -1;
                var liDemog_coverage = demographic_coverage[i] || 100;
                var liEfficacy = efficacy[i] || 1;
                // TODO need to pass in the supported models from existing
                // TODO intervention step data
                li_append(liID, liName, liStart_day, liNum_rep, liDays_between,
                        liDemog_coverage, liEfficacy, '');
            }
        }
    }
});


// String->array utility function (used to load the cart with previously
// selected interventions
function paramStringToArray(paramStr) {
    var s = paramString;
    s = s.replace(/\[/g, '');
    s = s.replace(/\]/g, '');
    s = s.replace(/&quot;/g, '');
    s = s.replace(/\s+/g, '');
    return s.split(",");
}



// Generates the labels that indicate which models are supported for each
// particular li_item (intervention)
function get_supported_model_labels_for_list_item(supported_model_csv) {
    model_names = supported_model_csv.split(',');
    o = '<div class="btn-group">'
    for (i in model_names) {
       o += '<div class="label label-inverse" style="margin:1px;">';
       o +=  model_names[i];
       o += '</div>';
    }
    o += '</div>';
    return o
}


// This function appends an li to the cart
function li_append(liID, liName, liStart_day, liNum_rep, liDays_between,
        liDemog_coverage, liEfficacy, liSupportedModelsCSV) {

    if ( $(this).not('.ui-draggable-dragging') ) {
        list_item = $(li_get(liID, liName, liStart_day, liNum_rep,
                    liDays_between, liDemog_coverage, liEfficacy,
                    liSupportedModelsCSV));

        $('ul.cart').append(list_item);
        $('.btn-small').tooltip({container:'body', placement:'top'});
    }
}

// This function is called each time a intervention is added to the cart,
// no matter how it was added. This keeps all formatting in one place.
//
//  idCounter:  (GLOBAL) unique id allows jQuery validation to know which
//              intervention to display the validation error messages in.
function li_get(liID, liName, liStart_day, liNum_rep, liDays_between,
        liDemog_coverage, liEfficacy, liSupportedModelsCSV) {

    box_style = ' style="width: 32px; height:11px;" '
    box_style_narrow = ' style="width: 21px; height:11px;" '

    my_li = '<li data-id="'+liID+ '">'
        + vsprintf('<strong class="pull-left">%s</strong>', [liName])

        + '<div id="list_item_button_toolbar" class="pull-right">'
        +  get_supported_model_labels_for_list_item(liSupportedModelsCSV)
        + '<button class="btn-small delete" style="position: static;" '
        +         'title="Remove this Intervention Event Instance">'
        +     '<i class="icon-remove"></i></button></div></br>'

        + '<div class="interventionDeploymentField">Start</br>Day:'
        + vsprintf('<input value="%s" type="text" name="%s" data-id="%s" %s id=%d>',
                [liStart_day, 'intervention-start_day', liID, box_style,
                    idCounter++])
        + '</div>'

        + '<div class="interventionDeploymentField">Number of</br>Distributions:'
        + vsprintf('<input value="%s" type="text" name="%s" data-id="%s" %s id=%d>',
                [liNum_rep, 'intervention-num_distributions', liID, box_style,
                    idCounter++])
        + '</div>'

        + '<div class="interventionDeploymentField">Days Between</br>Distributions:'
        + vsprintf('<input value="%s" type="text" name="%s" data-id="%s" %s id=%d>',
                [liDays_between, 'intervention-Timesteps_Between_Repetitions',
                    liID, box_style, idCounter++])
        + '</div>'

        + '<div class="interventionDeploymentField">Demographic</br>Coverage (%):'
        + vsprintf('<input value="%s" type="text" name="%s" data-id="%s" %s id=%d>',
                [liDemog_coverage, 'intervention-demographic_coverage', liID,
                    box_style, idCounter++])
        + '</div>'

//        + '<div class="interventionDeploymentField" id="efficacy_visibility">Efficacy:</br>&nbsp'
//        + '<input value="'+ liEfficacy +'" type="text" name="intervention-efficacy" data-id="'+ liID +'"' + box_style + 'id=efficacy_visibility>'
//        + '</div>'

        + '<div class="interventionDeploymentField" id="cost" >Cost per Covered</br>Individual ('
        + '<span id="currency" class="currency">$US</span>):'
        + vsprintf('<input value="%s" type="text" name="%s" data-id="%s" %s></div>',
                [liEfficacy, 'intervention-cost', liID, box_style])

        + vsprintf('<input type="hidden" name="intervention-interventions" value="%s:%s"/>',
                [liID, liName])
        + '</li>';
    return my_li;
}
//Provide validation for the fields
//var start_day_max = {{ start_day_max }} // set in template
$(document).ready(function(){
      $("#interventionForm").validate({
          rules: {
              "intervention-start_day": {
                  required: true,
                  range: [0, start_day_max]
                  /* digits: true,
                  min: 0,
                  max: start_day_max */
              },
              "intervention-num_distributions": {
                  required: true,
                  range: [1, 1000]
              },
              "intervention-Timesteps_Between_Repetitions": {
                  required: true,
                  range: [-1, 10000]
              },
              "intervention-demographic_coverage": {
                  required: true,
                  range: [0, 100]
              },
              "intervention-efficacy": {
                  required: true,
                  range: [0, 10000]
              },
          }
      });
});



/*######################################################################################################################
 # VECNet CI - Prototype
 # Date: 4/5/2013
 # Institution: University of Notre Dame
 # Primary Authors:
 #   Robert Jones <Robert.Jones.428@nd.edu>
 ######################################################################################################################*/
/* Javascript for ts_emod/views/ScenarioWizard Intervention Step */

/* Method to be executed when page has been loaded */
$(function () {

    /* Ensure that all tooltips are enabled (For backwards compatibility, include for: <a class="btn-small"> elements) */
    $('.tooltip_link').tooltip({container:'body', placement:'top', 'delay': { show: 500, hide: 500 }});
    $('.btn-small').tooltip({container:'body', placement:'top', 'delay': { show: 500, hide: 500 }});
    $('.run_button').tooltip({container:'body', placement:'top', 'delay': { show: 500, hide: 500 }});
    $('input').tooltip({container:'body', 'delay': { show: 500, hide: 500 }});  /* took out of browser.js - not sure where it's used, maybe could be removed */

    /* enable popovers - used on info button */
    $('.info').popover({placement: 'left', html: 'true', container: 'body'})
    $('.btn-preview').popover({placement: 'top', html: 'true', container: 'body',
                                template: '<div class="popover"><div class="arrow"></div><div class="popover-inner"><div class="popover-content"><p></p></div></div></div>'})

});

/* This closes a popover if you click anywhere not on the popover
   - side-effect: only one popover can be opened at a time
   - todo: turn button icon into red circle X close button
*/
$('body').on('click', function (e) {
    $('.info').each(function () {
        // 'is' for buttons that trigger popups
        // 'has' for icons within a button that triggers a popup
        if (!$(this).is(e.target) && $(this).has(e.target).length === 0 && $('.popover').has(e.target).length === 0) {
            $(this).popover('hide');
        }
    });

    $('.btn-preview').each(function () {
        // 'is' for buttons that trigger popups
        // 'has' for icons within a button that triggers a popup
        if (!$(this).is(e.target) && $(this).has(e.target).length === 0 && $('.popover').has(e.target).length === 0) {
            $(this).popover('hide');
        }
    });
});

/**
 *
 * Created by nreed on 12/8/14.
 */
$(function() {
    var runProgressBar = $("#run-progress");
    var totalSims = sims.length;
    var nrSimsFinished = 0.0;
    var intervNum = 0;
    var lookup = {};

    $.each(sims, function() {
        if (this.status == "done")
            nrSimsFinished++;

        lookup[this.id] = this;
    });

    if (nrSimsFinished != totalSims) {
        intervNum = setInterval(function () {
            $.get(sim_group_status_link, function (data) {
                var update = false;

                var ct = 0;
                $.each(data.sims, function () {
                    var old_sim = lookup[this.id];

                    if (old_sim.status != "done" && this.status == "done") {
                        nrSimsFinished++;
                        update = true;
                        lookup[this.id].status = "done";
                    }
                    ct++;
                });

                if (update) {
                    var percFinished = Math.floor((nrSimsFinished / totalSims) * 100);

                    if (nrSimsFinished >= totalSims) {
                        clearInterval(intervNum);

                        $("h3").html("Run Successful");
                        runProgressBar.removeClass("active");
                        $("#viz-results").show();
                    }

                    runProgressBar.children(".bar").animate({
                        width: percFinished + "%"
                    });

                    $("#run-progress-percent").html(percFinished + "%");

                    $("#finished-runs-count").html(nrSimsFinished);
                }
            });
        }, 10000);
    } else {
        runProgressBar.hide();
        $("h3").html("Run Successful");
        $("#finished-runs-count").html(nrSimsFinished);
        $("#viz-results").show();
    }
});
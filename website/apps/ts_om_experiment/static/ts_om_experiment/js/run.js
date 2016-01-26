/**
 *
 * Created by nreed on 12/8/14.
 */
$(function() {
    var totalSims = sims.length;
    var nrSimsFinished = 0.0;
    var intervNum = 0;
    var lookup = {};

    $.each(sims, function() {
        if (this.status == "done")
            nrSimsFinished++;

        lookup[this.id] = this;
    });

    var $h3 = $("h3");
    var $runProgressBar = $("#run-progress").children(".progress-bar");
    var $runPercent = $runProgressBar.children(".run-percent");
    var $screenReader = $runProgressBar.children(".sr-only");
    var $finishedRuns = $("#finished-runs-count");
    var $results = $("#viz-results");

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

                        $h3.html("Run Successful");
                        $runProgressBar.removeClass("active");
                        $results.show();
                    }

                    $runProgressBar.animate({
                        width: percFinished + "%"
                    }, {
                        step: function(now, fx) {
                            var floored_now = Math.floor(now);
                            $runPercent.html(floored_now + "%");
                            $screenReader.html(floored_now + "% Complete");
                        }
                    });

                    $finishedRuns.html(nrSimsFinished);
                }
            });
        }, 10000);
    } else {
        $runProgressBar.removeClass("active");
        $runPercent.html("100%");
        $screenReader.html("100% Complete");
        $runProgressBar.width("100%");

        $h3.html("Run Successful");
        $finishedRuns.html(nrSimsFinished);
        $results.show();
    }
});
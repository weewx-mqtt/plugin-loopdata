// Copyright (C)2022-2026 by John A Kline (john@johnkline.com)
// Distributed under the terms of the GNU Public License (GPLv3)
// See LICENSE for your rights.

  setPageExpirationTimer();
  setInterval(updateCurrent, refresh_rate * 1000);
  addLoadEvent(updateCurrent);

  async function updateCurrent() {
    if (pageTimedOut) {
      setUpExpiredClickListener();
      return false;
    }
    var response;
    try {
      response = await fetch('./loop-data.txt', {cache: 'no-store'});
    } catch (e) {
      // Network-level failure (server unreachable, request blocked): no
      // status to show.  A later successful poll rewrites the indicator.
      document.getElementById("live-label").innerHTML = fmt('OFFLINE');
      console.log(e);
      return;
    }
    if (!response.ok) {
      // The server answered but not with the file.  Almost always
      // loop_data_file not resolving to where loopdata writes -- the
      // classic being a 404 page because the file lives outside HTML_ROOT
      // (say /dev/shm) with nothing on the web server serving it.  Say so
      // in the indicator: the old behavior (a console error only a
      // debugging user ever finds) left the panel silently dead.
      document.getElementById("live-label").innerHTML =
          fmt('NO DATA (HTTP {status}) \u2014 check loop_data_file',
              {status: response.status});
      return;
    }
    var result;
    try {
      result = await response.json();
    } catch (e) {
      // A 200 with a non-json body: loop_data_file points at something,
      // but not at loopdata's output.
      document.getElementById("live-label").innerHTML =
          fmt('BAD DATA \u2014 check loop_data_file');
      console.log(e);
      return;
    }
    try {
      // The LIVE indicator, from the packet's own timestamp.
      var lastUpdate = new Date(result["current.dateTime.raw"] * 1000);
      var age = Math.round(Math.abs(new Date() - lastUpdate) / 1000);
      var element = document.getElementById("live-label");
      if (age <= 3 * refresh_rate) {
        element.innerHTML = fmt('LIVE');
      } else {
        element.innerHTML = fmt('{age}s ago', {age: age});
      }
      var activityElement = document.getElementById("last-update");
      activityElement.innerHTML = lastUpdate.toLocaleTimeString(LOCALE, {hour: '2-digit', minute:'2-digit', second:'2-digit'});

      updateGauges(result);
    } catch (e) {
      // A rendering error must not stop the polling; try again next
      // interval.
      console.log(e);
    }
  }


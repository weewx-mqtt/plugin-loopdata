// Copyright (C)2022-2026 by John A Kline (john@johnkline.com)
// Distributed under the terms of the GNU Public License (GPLv3)
// See LICENSE for your rights.

// Composed translations: look the English key up in T (falling back to
  // the key, so a missing entry renders English) and fill the {named}
  // placeholders.  Javascript key literals must spell non-ASCII with \u
  // escapes to match json.dumps' escaping of the generated object.
  function fmt(key, params) {
    var s = T[key] || key;
    for (var k in params) {
      s = s.replace('{' + k + '}', params[k]);
    }
    return s;
  }
  function addLoadEvent(func) {
    var oldonload = window.onload;
    if (typeof window.onload != 'function') {
      window.onload = func;
    } else {
      window.onload = function() {
        if (oldonload) {
          oldonload();
        }
        func();
      }
    }
  }
  function getUrlParam(paramName) {
      var name, regexS, regex, results;
      name = paramName.replace(/(\[|\])/g, '\\$1');
      regexS = '[\\?&]' + name + '=([^&#]*)';
      regex = new RegExp(regexS);
      results = regex.exec(window.location.href);
      if (results === null) {
          return '';
      } else {
          return results[1];
      }
  }
  var pageTimedOut = false;
  function expirePage() {
    pageTimedOut = true;
  }
  function setUpExpiredClickListener() {
    var liveLabel = document.getElementById("live-label");
    if (liveLabel != fmt('CLICK-ME')) {
      liveLabel.innerHTML = fmt('CLICK-ME');
      // set an onclick event on live-label to restart everything
      liveLabel.addEventListener("click", clickListener);
    }
  }
  function clickListener() {
    // disable the onClick event again
    var liveLabel = document.getElementById("live-label");
    liveLabel.removeEventListener('click', clickListener);
    liveLabel.innerHTML = "";
    // restart everything
    pageTimedOut = false;
    // restart the page timeout
    setPageExpirationTimer();
  }
  function setPageExpirationTimer() {
    if (getUrlParam('pageUpdate') !== page_update_pwd) {
      // expire in N hours
      setTimeout(expirePage, 1000 * 60 * 60 * expiration_time);
    }
  }


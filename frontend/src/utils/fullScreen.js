function fullScreen(element){
  var requestMethod = element.requestFullScreen || element.webkitRequestFullScreen || element.mozRequestFullScreen || element.msRequestFullScreen;
  if (requestMethod) {
      requestMethod.call(element);
  } else if (typeof window.ActiveXObject !== "undefined") {//for Internet Explorer
      var wscript = new ActiveXObject("WScript.Shell");
      if (wscript !== null) {
          wscript.SendKeys("{F11}");
      }
  }
}

function exitFullScreen() {
  var exitMethod = document.cancelFullScreen || document.webkitCancelFullScreen || document.mozCancelFullScreen || document.exitFullScreen;
  if (exitMethod) {
      exitMethod.call(document);
  } else if (typeof window.ActiveXObject !== "undefined") {
      var wscript = new ActiveXObject("WScript.Shell");
      if (wscript != null) {
          wscript.SendKeys("{F11}");
      }
  }
}

function isFullScreen(element) {
  return (
      element.fullscreen ||
      element.mozFullScreen ||
      element.webkitIsFullScreen ||
      element.webkitFullScreen ||
      element.msFullScreen
  );
}

export default {
  fullScreen, exitFullScreen, isFullScreen
}
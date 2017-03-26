// load and change settings via /cgi-bin/config.py
function setval(setting, value, callback) {
  var req = new XMLHttpRequest();
  req.onreadystatechange = function() {
    if(req.readyState == 4 && req.status == 200 && callback != null)
      callback(req.responseText);};
  req.open("GET", "/cgi-bin/config.py?setting=" + setting + "&value=" +  value);
  req.send(null);
}

// Handle global onload
function loadBase() {
  // Load Previews (Delayed)
  prevDivs = document.getElementsByClassName("preview");
  for (var i = 0; i < prevDivs.length; i++) {
    var prevImg = prevDivs[i].getElementsByTagName("img")[0];
    prevImg.onload = function() {
      this.classList.remove("hidden");
      this.parentNode.classList.remove("reservespace")
    };
    prevImg.src = "/cgi-bin/picture.py?type=thumb";
  }

  bigPrevs = document.getElementsByClassName("bigpreview");
  for (var i = 0; i < bigPrevs.length; i++) {
    bigPrevs[i].onload = function() {
      this.classList.remove("hidden");
      document.getElementsByClassName("spinnercenter")[0].classList.add("hidden");
    };
    bigPrevs[i].src = "/cgi-bin/picture.py";
  }

  // Call load of the page if it exists
  if(typeof load !== 'undefined' && load != null) load();
}
window.onload = loadBase;

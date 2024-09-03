
document.getElementsByTagName("head")[0].insertAdjacentHTML(
  "beforeend",
  "<link rel=\"stylesheet\" href=\"../reveal.js/dist/reveal.css\" />"
  +"<link rel=\"stylesheet\" href=\"../reveal.js/dist/theme/white.css\" />"  
  +"<link rel=\"stylesheet\" href=\"../resources/Font-Awesome/css/font-awesome.min.css\" />"
  +"<link rel=\"stylesheet\" href=\"../MCBreveal.css\" />"  
  +"<link rel=\"shortcut icon\" type=\"image/png\" href=\"favicon.png\">"
);

document.head.getElementsByTagName("link")[1].id="theme"

navigator.getUserMedia = ( navigator.getUserMedia ||
                       navigator.webkitGetUserMedia ||
                       navigator.mozGetUserMedia ||
                       navigator.msGetUserMedia);

function UpdateQueryString(key, value, url) {
  if (!url) url = window.location.href;
  var re = new RegExp("([?&])" + key + "=.*?(&|#|$)(.*)", "gi"),
      hash;

  if (re.test(url)) {
      if (typeof value !== 'undefined' && value !== null) {
          return url.replace(re, '$1' + key + "=" + value + '$2$3');
      } 
      else {
          hash = url.split('#');
          url = hash[0].replace(re, '$1$3').replace(/(&|\?)$/, '');
          if (typeof hash[1] !== 'undefined' && hash[1] !== null) {
              url += '#' + hash[1];
          }
          return url;
      }
  }
  else {
      if (typeof value !== 'undefined' && value !== null) {
          var separator = url.indexOf('?') !== -1 ? '&' : '?';
          hash = url.split('#');
          url = hash[0] + separator + key + '=' + value;
          if (typeof hash[1] !== 'undefined' && hash[1] !== null) {
              url += '#' + hash[1];
          }
          return url;
      }
      else {
          return url;
      }
  }
}

function TogglePrintable() {
    const urlSearchParams = new URLSearchParams(window.location.search);
    const params = Object.fromEntries(urlSearchParams.entries());
    if (params.hasOwnProperty("print-pdf"))
        window.location = UpdateQueryString("print-pdf");
    else
        window.location = UpdateQueryString("print-pdf", "");
}

function ToggleOverview() {
    Reveal.toggleOverview(true);
}

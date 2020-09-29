document.getElementsByTagName("head")[0].insertAdjacentHTML(
  "beforeend",
  "<link rel=\"stylesheet\" href=\"../reveal.js/dist/reveal.css\" />"
  +"<link rel=\"stylesheet\" href=\"../reveal.js/dist/theme/beige.css\" />"  
  +"<link rel=\"stylesheet\" href=\"../MCBreveal.css\" />"  
  +"<link rel=\"stylesheet\" href=\"../resources/Font-Awesome/css/font-awesome.min.css\" />"
  +"<link rel=\"shortcut icon\" type=\"image/png\" href=\"favicon.png\">"
);
document.head.getElementsByTagName("link")[1].id="theme"

navigator.getUserMedia = ( navigator.getUserMedia ||
                       navigator.webkitGetUserMedia ||
                       navigator.mozGetUserMedia ||
                       navigator.msGetUserMedia);

loadScripts = function (script_urls, script_callback) {
  var scripts_loaded = 0;
  script_urls.forEach(function(url) {
    var script = document.createElement('script');
    script.onload = function () {
      scripts_loaded++;
      if (scripts_loaded == script_urls.length)
	script_callback();
    };
    script.src = url;
    document.head.appendChild(script);
  });
};

loadScripts([
  "../reveal.js/dist/reveal.js",
  "../reveal.js/plugin/highlight/highlight.js",
  "../reveal.js/plugin/search/search.js",
  "../reveal.js/plugin/notes/notes.js",
  "../reveal.js/plugin/math/math.js",
  "../reveal.js-plugins/menu/menu.js",
],
	    function() {
	      var revealopts = {
		//This width and height allows printing to pdf at A4 and is slightly widescreen to give the best all round size
		width:1920,height:1080,margin:0.1, minScale:0.2, maxScale:1.5,
		slideNumber: 'c / t',
		history: true,
		transition: 'fade',
		backgroundTransition: 'fade',
		pdfMaxPagesPerSlide: 1,
		controls:false,
		plugins: [
		  RevealHighlight,
		  RevealSearch,
		  RevealNotes,
		  RevealMath,
		  RevealMenu
		],
		keyboard: {
		  67: function() { RevealChalkboard.toggleNotesCanvas() },	// toggle chalkboard when 'c' is pressed
		  66: function() { RevealChalkboard.toggleChalkboard() },	// toggle chalkboard when 'b' is pressed
		  46: function() { RevealChalkboard.clear() },	// clear chalkboard when 'DEL' is pressed
		  8:  function() { RevealChalkboard.reset() },	// reset all chalkboard data when 'BACKSPACE' is pressed
		  68: function() { RevealChalkboard.download() },	// downlad chalkboard drawing when 'd' is pressed
		  82: function() { Recorder.toggleRecording(); },	// press 'r' to start/stop recording
		  90: function() { Recorder.downloadZip(); }, 	// press 'z' to download zip containing audio files
		  84: function() { Recorder.fetchTTS(); } 	// press 't' to fetch TTS audio files		 
		},
		menu: {
		  titleSelector:'WILLNOTFINDTITLES',
		  markers: true,
		  hideMissingTitles: true,
		  themes: false,
		  transitions: false,
		  custom: [
		    { title: 'Lectures', icon: '<i class="fa fa-graduation-cap"></i>', src: 'toc.html' },
		  ]
		},
		chalkboard: { // font-awesome.min.css must be available
		  //src: "chalkboard/chalkboard.json",
		  toggleChalkboardButton: { left: "80px" },
			      toggleNotesButton: { left: "130px" },
		},
		math : {
		  //config: "TeX-AMS_HTML-full",
		  tex2jax: {
		    inlineMath: [['$','$'],['\\(','\\)']] ,
		    skipTags: ['script', 'noscript', 'style', 'textarea', 'pre']
		  },
		  TeX: { extensions: ["cancel.js"] }
		}
	      };
	      
	      Reveal.initialize(revealopts);
});

//var toc = $('.tableofcontents');
//if (toc.length) {
//    toc = toc[0];
//    $('div section')
//}

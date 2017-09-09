var link = document.createElement('link');
link.rel = 'stylesheet';
link.type = 'text/css';
if (window.location.search.match( /print-pdf/gi ))
    link.href = '../reveal.js/css/print/pdf.css';
else
    link.href = '../reveal.js/css/print/paper.css';
document.getElementsByTagName( 'head' )[0].appendChild( link );

head.load("../reveal.js/js/reveal.js", function() {
    Reveal.initialize({
	//This width and height allows printing to pdf at A4 and is slightly widescreen to give the best all round size
	width:1280,height:900,margin:0.1, minScale:0.2, maxScale:1.5,
	slideNumber: 'c / t',
	history: true,
	transition: 'slide',
	backgroundTransition: 'fade',
	pdfMaxPagesPerSlide: 1,
	controls:false,
	math: {
	    mathjax: '../MathJax/MathJax.js', 
	    config: 'TeX-AMS-MML_HTMLorMML'
	},
	dependencies: [
	    // Cross-browser shim that fully implements classList - https://github.com/eligrey/classList.js/
	    { src: '../reveal.js/lib/js/classList.js', condition: function() { return !document.body.classList; } },
	    // Syntax highlight for <code> elements
	    { src: '../reveal.js/plugin/highlight/highlight.js', async: true, callback: function() { hljs.initHighlightingOnLoad(); } },
	    // MathJax
	    { src: '../reveal.js/plugin/math/math.js', async: false},
	    { src: '../reveal.js-plugins/audio-slideshow/slideshow-recorder.js', condition: function( ) { return !!document.body.classList; } },
	    { src: '../reveal.js-plugins/audio-slideshow/audio-slideshow.js', condition: function( ) { return !!document.body.classList; } },
	    { src: '../reveal.js-plugins/chalkboard/chalkboard.js'},		 
	    { src: '../reveal.js-plugins/menu/menu.js'},
	],
	keyboard: {
	    67: function() { RevealChalkboard.toggleNotesCanvas() },	// toggle chalkboard when 'c' is pressed
	    66: function() { RevealChalkboard.toggleChalkboard() },	// toggle chalkboard when 'b' is pressed
	    46: function() { RevealChalkboard.clear() },	// clear chalkboard when 'DEL' is pressed
	    8: function() { RevealChalkboard.reset() },	// reset all chalkboard data when 'BACKSPACE' is pressed
	    68: function() { RevealChalkboard.download() },	// downlad chalkboard drawing when 'd' is pressed
	    82: function() { Recorder.toggleRecording(); },	// press 'r' to start/stop recording
	    90: function() { Recorder.downloadZip(); }, 	// press 'z' to download zip containing audio files
	    84: function() { Recorder.fetchTTS(); } 	// press 't' to fetch TTS audio files		 
	},
	menu: {
	    titleSelector:'h2, h3, h4, h5, h6',
	    markers: true,
	    hideMissingTitles: true,
	    themes: [
		{ name: 'Black', theme: '../reveal.js/css/theme/black.css' },
		{ name: 'White', theme: '../reveal.js/css/theme/white.css' },
		{ name: 'League', theme: '../reveal.js/css/theme/league.css' },
		{ name: 'Sky', theme: '../reveal.js/css/theme/sky.css' },
		{ name: 'Beige', theme: '../reveal.js/css/theme/beige.css' },
		{ name: 'Simple', theme: '../reveal.js/css/theme/simple.css' },
		{ name: 'Serif', theme: '../reveal.js/css/theme/serif.css' },
		{ name: 'Blood', theme: '../reveal.js/css/theme/blood.css' },
		{ name: 'Night', theme: '../reveal.js/css/theme/night.css' },
		{ name: 'Moon', theme: '../reveal.js/css/theme/moon.css' },
		{ name: 'Solarized', theme: '../reveal.js/css/theme/solarized.css' } ],
	    custom: [
		//{ title: 'Plugins', icon: '<i class="fa fa-external-link"></i>', src: 'toc.html' },
	    ]
	},
	chalkboard: { // font-awesome.min.css must be available
	    src: "chalkboard/chalkboard.json",
	    toggleChalkboardButton: { left: "80px" },
	    toggleNotesButton: { left: "130px" },
	},	     
    });
})
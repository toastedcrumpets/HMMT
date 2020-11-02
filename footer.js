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
    "../reveal.js-plugins/audio-slideshow/plugin.js",
    "../reveal.js-plugins/audio-slideshow/recorder.js",
    "../reveal.js-plugins/audio-slideshow/RecordRTC.js",
    "../reveal.js/plugin/highlight/highlight.js",
    "../reveal.js/plugin/search/search.js",
    "../reveal.js/plugin/notes/notes.js",
    "../reveal.js/plugin/math/math.js",
    "../reveal.js-plugins/menu/menu.js",
],
    function() {
	var revealopts = {
	    //This width and height allows printing to pdf at A4 and is slightly widescreen to give the best all round size
	    pdfSeparateFragments: false,
	    width:1920,
	    height:1080,
	    margin:0.1,
	    minScale:0.2,
	    maxScale:1.5,
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
		RevealMenu,
		RevealAudioSlideshow,
		RevealAudioRecorder
	    ],
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
		config: "TeX-AMS_SVG-full",
		tex2jax: {
		    inlineMath: [['$','$'],['\\(','\\)']] ,
		    skipTags: ['script', 'noscript', 'style', 'textarea', 'pre']
		},
		TeX: {
		    packages: {'[-]': ['require', 'autoload']},
		    extensions: ["cancel.js", "color.js"],
		    Macros: {
			bm: ["\\boldsymbol{#1}",1]
		    },
		},
	    }
	};

	if (!(typeof(audiofiles) === 'undefined')) {
	    //We have audio files, load the plugins
	    revealopts.plugins = revealopts.plugins.concat([
		RevealAudioSlideshow,
		RevealAudioRecorder
	    ]);
	    revealopts.audio = {
		prefix: audiofiles,
		autoplay:true,
	    }
	}

	
	Reveal.initialize(revealopts);
    }
	   );

//var toc = $('.tableofcontents');
//if (toc.length) {
//    toc = toc[0];
//    $('div section')
//}

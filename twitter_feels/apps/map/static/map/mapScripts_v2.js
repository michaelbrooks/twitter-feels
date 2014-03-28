(function(window) {

    var geocoder;
    var map;
    var markers = [];

    function initialize() {
        geocoder = new google.maps.Geocoder();
        var mapOptions =
        {
            center: new google.maps.LatLng(30.0, 0.0),
            zoom: 2,
            panControl: true,
            streetViewControl: false,
            zoomControl: true
        };

        map = new google.maps.Map(document.getElementById("map-canvas"), mapOptions);

        google.maps.event.addListener(map, 'click', function () {
            for (var i = 0; i < markers.length; i++) {
                markers[i].labelText = markers[i].originalWord;
                markers[i].labelClass = "labels";
                markers[i].setMap(map);
            }

            document.getElementById("pronouns").innerHTML = "";
            document.getElementById("verbs").innerHTML = "";
            document.getElementById("info").innerHTML = "";
        });
    }

    function showVerbDropdown() {
        var pronouns = document.getElementById("pronouns");
        if (pronouns.innerHTML != "") {
            pronouns.innerHTML = "";
        }

        var verbs = document.getElementById("verbs");
        if (verbs.innerHTML == "") {
            var text = '<div class="dropdown"><ul class="dropDown">';
            text += '<li class="dropDown">want</li>';
            text += '<li class="dropDown">need</li>';
            text += '<li class="dropDown">feel</li></ul></div>';

            verbs.innerHTML = text;
        }
        else {
            verbs.innerHTML = "";
        }
    }

    function showPronounDropdown() {
        var verbs = document.getElementById("verbs");
        if (verbs.innerHTML != "") {
            verbs.innerHTML = "";
        }

        var pronouns = document.getElementById("pronouns");
        if (pronouns.innerHTML == "") {
            var text = '<div class="dropdown">';
            text += '<ul class="dropDown">';
            text += '<li class="dropDown">I</li>';
            text += '<li class="dropDown">We</li>';
            text += '<li class="dropDown">They</li></ul></div>';

            pronouns.innerHTML = text;
        }
        else {
            pronouns.innerHTML = "";
        }
    }

    function setPronoun(text) {
        document.getElementById("selectedPronoun").innerHTML = text;
        document.getElementById("pronouns").innerHTML = "";
    }

    function setVerb(text) {
        document.getElementById("selectedVerb").innerHTML = text;
        document.getElementById("verbs").innerHTML = "";
    }

    var req_fifo;

    function GetAsyncData(url, gotDataCallback, parameter) {
        if (window.XMLHttpRequest) {
            req_fifo = new XMLHttpRequest();
            req_fifo.abort();
            req_fifo.onreadystatechange = function () {
                if (req_fifo.readyState == 4 && req_fifo.status == 200) {
                    gotDataCallback(parameter);
                }
            };

            req_fifo.open("GET", url, true);
            req_fifo.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
            req_fifo.send();
        }
        else if (window.ActiveXObject) {
            req_fifo = new ActiveXObject("Microsoft.XMLHTTP");
            if (req_fifo) {
                req_fifo.abort();
                req_fifo.onreadystatechange = function () {
                    if (req_fifo.readyState == 4 && req_fifo.status == 200) {
                        gotDataCallback(parameter);
                    }
                };

                req_fifo.open("GET", url, true);
                req_fifo.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
                req_fifo.send();
            }
        }
    }

    function submitQuery() {
        for (var i = 0; i < markers.length; i++) {
            markers[i].setMap(null);
        }

        markers = [];

        // Uncomment for local debugging
    //     var url = "placeholder.php";
        //var url = "query_v2.php" + queryString();
        //var url = "http://nanchen.csie.org/~twitter-feels-map/query_v2.php" + queryString();
        var url = "/map/faster_query.json" + queryString();
        GetAsyncData(url, gotMapData, null);
    }

    function queryString() {
        var query = "?q=" + document.getElementById("selectedPronoun").innerHTML + " " + document.getElementById("selectedVerb").innerHTML;
        var queryTail = document.getElementById("nextWords").value.trim();
        if (queryTail != "") {
            query = query + " " + queryTail;
        }

        return encodeURI(query);
    }

    function queryStringCountry(marker) {
        return encodeURI(" " + marker.originalWord + "&country=" + marker.country.split(' ').join(' '));
    }

    function toggleSampleTweet(marker) {
        if (marker.labelText.toLowerCase() == marker.originalWord.toLowerCase()) {
            // Uncomment for local debugging
            //var url = "sample_tweets_v2.php" + queryString() + queryStringCountry(marker);
            var url = "/map/example_tweet.json" + queryString() + queryStringCountry(marker);
            GetAsyncData(url, gotTweet, marker);
        }
        else {
            marker.labelClass = labelClassNameForText(marker.originalWord);
            marker.labelText = marker.originalWord;
            marker.setMap(map);
        }
    }

    function labelClassNameForText(text)
    {
        return text.length < 9 ? "labels" : "labelsLong";
    }

    function gotTweet(marker) {
        marker.labelClass = "labels2";
        marker.labelText = "<span class='tweet-text'>" + JSON.parse(req_fifo.responseText) + "</span>" +
            "<span class='twitter-icon'></span>" +
            "<span class='glyphicon glyphicon-remove'></span>";
        marker.setMap(map);
    }

    function gotMapData(p) {
        var jsonData = JSON.parse(req_fifo.responseText);
        for (var i = 0; i < jsonData.words.length; i++) {
            var country = jsonData.words[i].country;
            var text = jsonData.words[i].text;

            geocoder.geocode(
                { 'address': country },
                function (captured_text, captured_country) {
                    return function (results, status) {
                        if (status == google.maps.GeocoderStatus.OK) {
                            var labelClassName = labelClassNameForText(captured_text);
                            var marker = new MarkerWithLabel({
                                position: results[0].geometry.location,
                                draggable: false,
                                map: map,
                                labelText: captured_text.toLowerCase(),
                                labelClass: labelClassName,//"labels", // the CSS class for the label
                                labelStyle: { top: "0px", left: "-21px", opacity: 0.80 },
                                labelVisible: true,
                                country: captured_country,
                                originalWord: captured_text.toLowerCase()
                            });

                            markers.push(marker);
                            google.maps.event.addListener(marker, "click", function () { toggleSampleTweet(marker); });
                        }
                    }
                } (text, country));
        }
    }

    function toggleInfo() {
        var info = document.getElementById("info");
        if (info.innerHTML == "") {
            var text = "<div id='infoContainer'>";
            text += "<ul id='infoList'><li class='info'>Start building a tweet phrase by selecting a subject (I/we/they) and a verb (want/need/feel) from the drop down lists</li>";
            text += "<li>Type in the text box to add to the tweet phrase</li>";
            text += '<li>Click on the search button or hit enter, and you will see gray shaded tweet boxes pinpointing the "top ten" countries in which your phrase originated</li>';
            text += '<li>Each tweet box shows the word that most frequently follows your phrase in that country</li>';
            text += '<li>Click on the tweet box to see a randomly selected example tweet</li>';
            text += "</ul></div>";


            info.innerHTML = text;
        }
        else {
            info.innerHTML = "";
        }
    }

    $(document).ready(function () {
        submitQuery();
        $("#form").submit(function (e) {

            e.preventDefault();
            submitQuery();

        });

        $('.pronounDropdown').click(showPronounDropdown);
        $('.verbDropdown').click(showVerbDropdown);
        $('.info-button-box').click(toggleInfo);

        $('#verbs').on('click', 'li', function(e) {
            setVerb($(this).text());
        });

        $('#pronouns').on('click', 'li', function(e) {
            setPronoun($(this).text());
        });
    });

    window.initialize_map = initialize;

})(window);

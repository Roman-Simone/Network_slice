function eseguiAllAperturaPagina(){
    changeScenario("default")
}

function changeScenario(scenario) {
    document.querySelectorAll('.button-bar button').forEach(function (btn) {
        btn.classList.remove('active');
    });

    document.getElementById(scenario + 'Btn').classList.add('active');

    sendRequest(scenario);

    var xhr = new XMLHttpRequest();
    xhr.open("GET", "http://192.168.64.16:8000/changeScenario/?data=" + scenario, true);
    xhr.onreadystatechange = function() {
    if (xhr.readyState === 4 && xhr.status === 200) {
        var response = JSON.parse(xhr.responseText);
        console.log(response);
        
    }
    };
    xhr.send();
    refreshAll()
}
// GET http://192.168.64.16:8000/changeScenario/?data=scenario2/ net::ERR_INTERNET_DISCONNECTED
function cleanTable(){
    for (var i = 0; i < 6; i++) {
        document.getElementById("speed1_"+i).innerHTML = "-"
        document.getElementById("speed2_"+i).innerHTML = "-"
        document.getElementById("speed1UDP_"+i).innerHTML = "-"
        document.getElementById("speed2UDP_"+i).innerHTML = "-"
    }
}
function refreshAll(){
    // cleanTable()
    refreshTCP()
    console.log("sium1")
    refreshUDP()
    console.log("sium2")
}
function refreshTCP(){
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "http://192.168.64.16:8000/get/throughput/tcp/", true);
    xhr.onreadystatechange = function() {
    if (xhr.readyState === 4 && xhr.status === 200) {
        var response = JSON.parse(xhr.responseText);
        
        var networkData = response.network
        
        for (var i = 0; i < response.network.length; i++) {
            var entry = networkData[i];
            var speed1 = entry.host1.speed;
            var speed2 = entry.host2.speed;
            document.getElementById("speed1_"+i).innerHTML = speed1 + ""
            document.getElementById("speed2_"+i).innerHTML = speed2 + ""
        }
        
    }
    
    };
    xhr.send();
}
function refreshUDP(){
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "http://192.168.64.16:8000/get/throughput/udp/", true);
    xhr.onreadystatechange = function() {
    if (xhr.readyState === 4 && xhr.status === 200) {
        
        var response = JSON.parse(xhr.responseText);
        var networkData = response.network
        console.log(response)
        console.log(response.network.length)
        for (var i = 0; i < response.network.length; i++) {
            var entry = networkData[i];
            var speed1 = entry.host1.speed;
            var speed2 = entry.host2.speed;
            document.getElementById("speed1UDP_"+i).innerHTML = speed1 + ""
            document.getElementById("speed2UDP_"+i).innerHTML = speed2 + ""
        }
        
    }
    
    };
    xhr.send();
}

var jsonData = {   //poi sarà da leggere la risposta 
    "network": [
        {
            "host1": { "name": "h1", "speed": "-" },
            "host2": { "name": "h3", "speed": "-" }
        },
        {
            "host1": { "name": "h2", "speed": "-" },
            "host2": { "name": "h4", "speed": "-" }
        },
        {
            "host1": { "name": "h1", "speed": "-" },
            "host2": { "name": "h4", "speed": "-" }
        },
        {
            "host1": { "name": "h2", "speed": "-" },
            "host2": { "name": "h3", "speed": "-" }
        },
        {
            "host1": { "name": "h5", "speed": "-" },
            "host2": { "name": "h6", "speed": "-" }
        },
        {
            "host1": { "name": "h7", "speed": "-" },
            "host2": { "name": "h8", "speed": "-" }
        }
    ]
};
var jsonDataUDP = {
    "network": [
        {
            "host1": {"name": "h1", "speed": "-"},
            "host2": {"name": "h3", "speed": "-"}
        },
        {
            "host1": {"name": "h2", "speed": "-"},
            "host2": {"name": "h4", "speed": "-"}
        },
        {
            "host1": {"name": "h1", "speed": "-"}, 
            "host2": {"name": "h4", "speed": "-"}}, 
        {
            "host1": {"name": "h2", "speed": "-"}, 
            "host2": {"name": "h3", "speed": "-"}
        }, 
        {
            "host1": {"name": "h5", "speed": "-"},
            "host2": {"name": "h6", "speed": "-"}
        }, 
        {
            "host1": {"name": "h7", "speed": "-"}, 
            "host2": {"name": "h8", "speed": "-"}
        }
    ]
}

var networkData = jsonData.network;
var networkDataUDP = jsonDataUDP.network
var output = "";
for (var i = 0; i < networkData.length; i++) {
    var entry = networkData[i];
    var host1 = entry.host1.name;
    var host2 = entry.host2.name;
    var speed1 = entry.host1.speed;
    var speed2 = entry.host2.speed;

    var entryUDP = networkDataUDP[i];
    var host1UDP = entryUDP.host1.name;
    var host2UDP = entryUDP.host2.name;
    var speed1UDP = entryUDP.host1.speed;
    var speed2UDP = entryUDP.host2.speed;
   

    output += "<div class='col-md-6'>";
    output += "<div class='card mb-4'>";
    output += "<div class='card-header'><center><b>" + host1 + " ----> " + host2 + "</b></center></div>";
    output += "<table class='table'>";
    
    
    if(host1 == "h1" && host2== "h3" || host1 == "h1" && host2== "h4" || host1 == "h2" && host2== "h4" || host1 == "h2" && host2== "h3"){
        output += "<thead><tr><th>Host</th><th>Speed (TCP)</th><th>Speed (UDP)</th></tr></thead>";
        output += "<tbody>";
        output += "<tr><td class=\"text-white\">" + host1 + "</td><td id=\"speed1_"+i+"\" class=\"text-white\">" + speed1 + "</td><td id=\"speed1UDP_"+i+"\" class=\"text-white\">" + speed1UDP + "</td></tr>";
        output += "<tr><td class=\"text-white\">" + host2 + "</td><td id=\"speed2_"+i+"\" class=\"text-white\">" + speed2 + "</td><td id=\"speed2UDP_"+i+"\" class=\"text-white\">" + speed2UDP + "</td></tr>";
    }
    else {
        output += "<thead><tr><th>Host</th><th>Speed (TCP)</tr></thead>";
        output += "<tbody>";
        output += "<tr><td class=\"text-white\">" + host1 + "</td><td id=\"speed1_"+i+"\" class=\"text-white\">" + speed1 + "</td></tr>";
        output += "<tr><td class=\"text-white\">" + host2 + "</td><td id=\"speed2_"+i+"\" class=\"text-white\">" + speed2 + "</td></tr>";
    } 
    
    output += "</tbody>";
    output += "</table>";
    output += "</div>";
    output += "</div>";
}

document.getElementById("output").innerHTML = output;

function sendRequest(requestName) {
    switch (requestName) {
        case 'default':
            // invio richiesta HTML per attivazione scenario default
            var image = document.querySelector('#scenario_image img');
            image.src = "https://raw.githubusercontent.com/Sro552/network_slice/main/WebApp/images/Scenario_0_Lower.png";
            console.log('Scenario default selezionato');

            break;
        case 'scenario1':
            // invio richiesta HTML per attivazione scenario lower
            var image = document.querySelector('#scenario_image img');
            image.src = "https://github.com/Sro552/network_slice/blob/main/WebApp/images/Scenario_1_Lower.png?raw=true";
            console.log('Scenario lower selezionato');
            break;
        case 'scenario2':
             // invio richiesta HTML per attivazione scenario higher
            var image = document.querySelector('#scenario_image img');
            image.src = "https://github.com/Sro552/network_slice/blob/main/WebApp/images/Scenario_2_Upper.png?raw=true";
            console.log('Scenario higher selezionato');
            break;
        case 'scenario3':
            // invio richiesta HTML per attivazione scenario total
            var image = document.querySelector('#scenario_image img');
            image.src = "https://github.com/Sro552/network_slice/blob/main/WebApp/images/Scenario_3_Total.png?raw=true";
            console.log('Scenario total selezionato');
            break;
        default:
            console.log('Errore nella richiesta');
    }
}
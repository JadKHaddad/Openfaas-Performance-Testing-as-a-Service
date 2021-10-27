FUNCTIONCALL = '/proxy'



function showInfo(message, color) {
    if (color == null){
        $('#info-message').addClass('red');
    }else{
        $('#info-message').addClass(color);
    }
    // set message
    $('#info-message').text(message);
    // show message
    $('#info-modal-button').click();
}

function setUpCode(code) {
    // set code
    $('#code').text(code);
    // show code
    $('#code-modal-button').click();
}

function setConfirmationModal(message, func, buttonText) {
    // set message
    $('#confirm-message').text(message);
    // unbind
    $('#confirm-delete').off('click');
    // bind
    $('#confirm-delete').on('click', function () {
        func();
    });
    if (buttonText != null){
        $('#confirm-delete').html(buttonText);
    }
    // show
    $('#confirmation-modal-button').click();
}

function isInteger(str) {
    var pattern = /^\d+$/;
    return pattern.test(str);
}

function IsJsonString(str) {
    try {
        JSON.parse(str);
    } catch (e) {
        return false;
    }
    return true;
}

function getHostName(urlStr){
    var l = new URL(urlStr)
    return l.hostname + ':' + l.port;
}

function setCookie(name, value, daysToLive) {
    // Encode value in order to escape semicolons, commas, and whitespace
    var cookie = name + "=" + encodeURIComponent(value);
    
    if(typeof daysToLive === "number") {
        /* Sets the max-age attribute so that the cookie expires
        after the specified number of days */
        cookie += "; max-age=" + (daysToLive*24*60*60) + ";path=/";
        
        document.cookie = cookie;
    }
}

function getCookie(name) {
    // Split cookie string and get all individual name=value pairs in an array
    var cookieArr = document.cookie.split(";");
    
    // Loop through the array elements
    for(var i = 0; i < cookieArr.length; i++) {
        var cookiePair = cookieArr[i].split("=");
        
        /* Removing whitespace at the beginning of the cookie name
        and compare it with the given string */
        if(name == cookiePair[0].trim()) {
            // Decode the cookie value and return
            return decodeURIComponent(cookiePair[1]);
        }
    }
    // Return null if not found
    return null;
}

document.addEventListener("DOMContentLoaded", function () {
    const functionName = document.getElementById('function-name').innerText;
    var openfaasUrl = document.getElementById('openfaas-url').innerText;
    var direct = false;
    if (document.getElementById('direct').innerText === 'true') direct = true;

    if (getCookie('openfaasurl') != null){
        openfaasUrl = getCookie('openfaasurl');
    }

    if (getCookie('direct') != null){
        direct = false;
        if(getCookie('direct') === 'true') direct = true;
    }

    if (getCookie('theme') != null){
        if(getCookie('theme') === 'dark') {
            $('#dark-theme-checkbox').prop('checked', true);
        };
    }

    $('#url-input').val(openfaasUrl);
    $('#url').text(openfaasUrl);
    $('#nav-url').on('click', function(){
        $('#url-modal-button').click();
        return false;
    });

    $('#set-url-btn').on('click',function(){
        openfaasUrl = $('#url-input').val();
        openfaasUrl = openfaasUrl.replace("http://", "").replace("https://", "");
        openfaasUrl = "http://" + openfaasUrl;
        direct = false;
        if($('#direct-checkbox').prop('checked') == true) direct = true; 
        if($('#no-openfaas-checkbox').prop('checked') == true) openfaasUrl = 'None';
        setCookie('direct', direct.toString(), 365);
        setCookie('openfaasurl', openfaasUrl, 365);
        theme = 'light'
        if($('#dark-theme-checkbox').prop('checked') == true) theme = 'dark'; 
        setCookie('theme', theme, 365);

        if (openfaasUrl === 'None'){
            FUNCTIONCALL = '/local';
        }else if (direct){
            if (openfaasUrl.slice(-1) == '/'){
                openfaasUrl = openfaasUrl.slice(0, -1);
            }
            FUNCTIONCALL = `${openfaasUrl}/function/${functionName}`;
        }
        location.reload(true);
    });

    $('#no-openfaas-checkbox').change(function() {
        if($(this).prop('checked') == true){
            $('#url-input').prop('disabled', true);
            $('#direct-checkbox').prop('disabled', true);
        }else{
            $('#url-input').prop('disabled', false);
            $('#direct-checkbox').prop('disabled', false);
        }
    }); 

    $('#restore-defaults-btn').on('click', function(){
        setCookie('direct', direct.toString(), -1);
        setCookie('openfaasurl', openfaasUrl, -1);
        location.reload(); 
    });

    setCookie('openfaasurl', openfaasUrl, 365);
    
    if (openfaasUrl === 'None'){
        FUNCTIONCALL = '/local';
        $('#direct-checkbox').prop('disabled', true);
        $('#no-openfaas-checkbox').prop('checked', true);
    }else if (direct){
        if (openfaasUrl.slice(-1) == '/'){
            openfaasUrl = openfaasUrl.slice(0, -1);
        }
        FUNCTIONCALL = `${openfaasUrl}/function/${functionName}`;
        $('#direct-checkbox').prop('disabled', false);
        $('#direct-checkbox').prop('checked', true);
    }

    if($('#no-openfaas-checkbox').prop('checked') == true){
        openfaasUrl = 'None';
        $('#url-input').prop('disabled', true);
    }else{
        $('#url-input').prop('disabled', false);
    }
});

console.log("skypeManage.js");
function listenMessage(request, sender, sendResponse) {
    if(request.action == "getData"){
        var clientName = request.clientName;
        var return_data = {};
        return_data.active_time_arr = getTimeToArray(clientName, "active_time");
        return_data.chat_time_arr = getTimeToArray(clientName, "chat_time");
        sendResponse({ "success": true, data: return_data });
        return true;
    }
    else if(request.action == "getClientName") {
        var client_arr = get_client_name();
        sendResponse({ data: client_arr, url: document.location.href });
    }
    else if(request.action == "initData") {
        var clientName = request.clientName;
        for (var key in localStorage) {
            if (Object.hasOwnProperty.call(localStorage, key)) {
                if(key.search("skype_" + clientName) > -1)
                localStorage[key] = 0;
            }
        }
    }
}
window.onload = function(){
    chrome.extension.onMessage.addListener(listenMessage);
    if(document.location.href.indexOf("web.skype.com") == -1)
        return;
    saveActiveTime();
    window.setInterval(saveActiveTime,600000);
    $(document).on("click", function(){
        save_chat_time();
    });
};

function get_client_name() {
    var obj = $("[style='position: relative; display: flex; flex-direction: column; flex-grow: 1; flex-shrink: 1; overflow: hidden; align-items: stretch; align-self: stretch; background-color: rgba(0, 0, 0, 0);']");
    var return_arr = [];
    obj.find("div[id^='rx-vlv-']").each(function(){
        var text = $(this).attr("aria-label");
        if(!text)
            return;
        var data_arr = text.split(", ");
        if(data_arr[0] != "favorite")
            return;
        var name = data_arr[1];
        return_arr.push(name);
    });
    return return_arr;
}

function saveActiveTime(){
    var curDay = new Date();
    var curTime = curDay.getHours();
    var obj = $("[style='position: relative; display: flex; flex-direction: column; flex-grow: 1; flex-shrink: 1; overflow: hidden; align-items: stretch; align-self: stretch; background-color: rgba(0, 0, 0, 0);']");
    var return_arr = [];
    obj.find("div[id^='rx-vlv-']").each(function(){
        var text = $(this).attr("aria-label");
        if(!text)
            return;
        var data_arr = text.split(", ");
        if(data_arr[0] != "favorite")
            return;
        if(data_arr[2].indexOf("Active now") == -1)
            return;
        var name = data_arr[1];
        if(localStorage['skype'+ "_" + name + "_" +'active_time'+ "_" +curTime]){
            var init_val = parseInt(localStorage['skype'+ "_" + name + "_" +'active_time'+ "_" +curTime]);
            if(isNaN(init_val))
                localStorage['skype'+ "_" + name + "_" +'active_time'+ "_" +curTime] = 0;
            if(localStorage['skype'+ "_" + name + "_" +'active_time'+ "_" +curTime] < 999)
                localStorage['skype'+ "_" + name + "_" +'active_time'+ "_" +curTime] = init_val + 1;
        }
        else {
            localStorage['skype'+ "_" + name + "_" +'active_time'+ "_" +curTime] = 0;
        }
    });
    return;
}

function getTimeToArray(clientName, type = "active_time"){
    var result_arr = [];
    for (var i = 0; i < 24; i++) {
        if(localStorage['skype'+ "_" + clientName + "_" +type+ "_" +i])
            result_arr.push(localStorage['skype'+ "_" + clientName + "_" +type+ "_" + i]);
        else
            result_arr.push(0);
    }
    return result_arr;
}

function save_chat_time(){
    var obj = $("[style='position: relative; display: flex; flex-direction: column; flex-grow: 1; flex-shrink: 1; overflow: hidden; align-items: stretch; align-self: stretch; background-color: rgba(0, 0, 0, 0);']");
    var selected_obj = obj.find("div[id^='rx-vlv-'][tabindex='0']");
    if(selected_obj.length == 0)
        return;
    var text = selected_obj.attr("aria-label");;
    if(!text)
        return;
    var data_arr = text.split(", ");
    if(data_arr[0] != "favorite")
        return;
    var name = data_arr[1];

    var time_obj = $("[style='position: relative; display: inline; flex-grow: 1; flex-shrink: 1; overflow: hidden; white-space: pre; text-overflow: ellipsis; background-color: rgba(0, 0, 0, 0); align-self: center; padding-bottom: 25px; font-size: 12px; color: rgb(138, 141, 145); font-family: \"SF Regular\", \"Segoe System UI Regular\", \"Segoe UI Regular\", sans-serif; font-weight: 400; user-select: text; cursor: text;");
    time_obj.each(function(){
        var text = $(this).text();
        var text_arr = text.split(", ");
        var time_str = text_arr[1];
        var hour = parseInt(time_str.split(":")[0]);
        if(isNaN(hour))
            return;
        if(hour == 12)
            hour = 0;
        var day_or_night = time_str.substr(-2);
        if(day_or_night.toUpperCase() == "PM")
            hour += 12;
        var curTime = hour;

        // save temp data
        var parent_text = $(this).parent().parent().parent().parent().parent().attr("aria-label").substr(0,30);
        if(localStorage['skype'+ "_" + name + "_" +'chat_time'+ "_temp"]){
            if(localStorage['skype'+ "_" + name + "_" +'chat_time'+ "_temp"].length > 3000){
                localStorage['skype'+ "_" + name + "_" +'chat_time'+ "_temp"] = localStorage['skype'+ "_" + name + "_" +'chat_time'+ "_temp"].substr[100];
            }
            if(localStorage['skype'+ "_" + name + "_" +'chat_time'+ "_temp"].indexOf(parent_text) == -1)
                localStorage['skype'+ "_" + name + "_" +'chat_time'+ "_temp"] += parent_text;
            else
                return;
        }
        else {
            localStorage['skype'+ "_" + name + "_" +'chat_time'+ "_temp"] = parent_text;
        }

        // set new data
        if(localStorage['skype'+ "_" + name + "_" +'chat_time'+ "_" +curTime]){
            var init_val = parseInt(localStorage['skype'+ "_" + name + "_" +'chat_time'+ "_" +curTime]);
            if(isNaN(init_val))
                localStorage['skype'+ "_" + name + "_" +'chat_time'+ "_" +curTime] = 0;
            if(localStorage['skype'+ "_" + name + "_" +'chat_time'+ "_" +curTime] < 999)
                localStorage['skype'+ "_" + name + "_" +'chat_time'+ "_" +curTime] = init_val + 1;
        }
        else {
            localStorage['skype'+ "_" + name + "_" +'chat_time'+ "_" +curTime] = 0;
        }
    })
    return;
    
}
const zero_data = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0];
const test_data = [1,2,3,4,5,6,7,8,9,10,11,12,11,10,9,8,7,6,5,4,3,2,1,0,1];
window.onload = function() {
    get_client_name();
    init_chat(zero_data,zero_data);
}

function init_chat(active_time_arr, chat_time_arr) {
    $(document).show();
    if(!active_time_arr || active_time_arr.length == 0)
        active_time_arr = test_data;
    if(!chat_time_arr || chat_time_arr.length == 0)
        chat_time_arr = test_data;
    var active_time_element = document.getElementById("active_time_chart");
    active_time_element.innerHTML = "";
    if (active_time_element) {
        var active_setting = {
            series: [{
                name: "Active time",
                data: active_time_arr
            }],
            chart: {
                type: "area",
                height: 200,
                toolbar: {
                    show: !1
                }
            },
            plotOptions: {},
            legend: {
                show: !1
            },
            dataLabels: {
                enabled: !1
            },
            fill: {
                type: "solid",
                opacity: 1
            },
            stroke: {
                curve: "smooth",
                show: !0,
                width: 3,
                colors: [KTAppSettings.colors.theme.base.info]
            },
            xaxis: {
                categories: ["12:00 AM", "1:00 AM", "2:00 AM", "3:00 AM", "4:00 AM", "5:00 AM", "6:00 AM", "7:00 AM", "8:00 AM", "9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "1:00 PM", "2:00 PM", "3:00 AM", "4:00 PM", "5:00 PM", "6:00 PM", "7:00 PM", "8:00 PM", "9:00 PM", "10:00 PM", "11:00 PM"],
                axisBorder: {
                    show: !1
                },
                axisTicks: {
                    show: !1
                },
                labels: {
                    style: {
                        colors: KTAppSettings.colors.gray["gray-500"],
                        fontSize: "12px",
                        fontFamily: KTAppSettings["font-family"]
                    }
                },
                crosshairs: {
                    position: "front",
                    stroke: {
                        color: KTAppSettings.colors.theme.base.info,
                        width: 1,
                        dashArray: 3
                    }
                },
                tooltip: {
                    enabled: !0,
                    formatter: void 0,
                    offsetY: 0,
                    style: {
                        fontSize: "12px",
                        fontFamily: KTAppSettings["font-family"]
                    }
                }
            },
            yaxis: {
                labels: {
                    style: {
                        colors: KTAppSettings.colors.gray["gray-500"],
                        fontSize: "12px",
                        fontFamily: KTAppSettings["font-family"]
                    }
                }
            },
            states: {
                normal: {
                    filter: {
                        type: "none",
                        value: 0
                    }
                },
                hover: {
                    filter: {
                        type: "none",
                        value: 0
                    }
                },
                active: {
                    allowMultipleDataPointsSelection: !1,
                    filter: {
                        type: "none",
                        value: 0
                    }
                }
            },
            tooltip: {
                style: {
                    fontSize: "12px",
                    fontFamily: KTAppSettings["font-family"]
                },
                y: {
                    formatter: function(t) {
                        return t + " %"
                    }
                }
            },
            colors: [KTAppSettings.colors.theme.light.info],
            grid: {
                borderColor: KTAppSettings.colors.gray["gray-200"],
                strokeDashArray: 4,
                yaxis: {
                    lines: {
                        show: !0
                    }
                }
            },
            markers: {
                strokeColor: KTAppSettings.colors.theme.base.info,
                strokeWidth: 3
            }
        };
        new ApexCharts(active_time_element, active_setting).render()
    }
    var chat_time_element = document.getElementById("chat_time_chart");
    chat_time_element.innerHTML = "";
    if (chat_time_element) {
        var chat_setting = {
            series: [{
                name: "Chat time",
                data: chat_time_arr
            }],
            chart: {
                type: "area",
                height: 200,
                toolbar: {
                    show: !1
                }
            },
            plotOptions: {},
            legend: {
                show: !1
            },
            dataLabels: {
                enabled: !1
            },
            fill: {
                type: "solid",
                opacity: 1
            },
            stroke: {
                curve: "smooth",
                show: !0,
                width: 3,
                colors: [KTAppSettings.colors.theme.base.info]
            },
            xaxis: {
                categories: ["12:00 AM", "1:00 AM", "2:00 AM", "3:00 AM", "4:00 AM", "5:00 AM", "6:00 AM", "7:00 AM", "8:00 AM", "9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "1:00 PM", "2:00 PM", "3:00 AM", "4:00 PM", "5:00 PM", "6:00 PM", "7:00 PM", "8:00 PM", "9:00 PM", "10:00 PM", "11:00 PM"],
                axisBorder: {
                    show: !1
                },
                axisTicks: {
                    show: !1
                },
                labels: {
                    style: {
                        colors: KTAppSettings.colors.gray["gray-500"],
                        fontSize: "12px",
                        fontFamily: KTAppSettings["font-family"]
                    }
                },
                crosshairs: {
                    position: "front",
                    stroke: {
                        color: KTAppSettings.colors.theme.base.info,
                        width: 1,
                        dashArray: 3
                    }
                },
                tooltip: {
                    enabled: !0,
                    formatter: void 0,
                    offsetY: 0,
                    style: {
                        fontSize: "12px",
                        fontFamily: KTAppSettings["font-family"]
                    }
                }
            },
            yaxis: {
                labels: {
                    style: {
                        colors: KTAppSettings.colors.gray["gray-500"],
                        fontSize: "12px",
                        fontFamily: KTAppSettings["font-family"]
                    }
                }
            },
            states: {
                normal: {
                    filter: {
                        type: "none",
                        value: 0
                    }
                },
                hover: {
                    filter: {
                        type: "none",
                        value: 0
                    }
                },
                active: {
                    allowMultipleDataPointsSelection: !1,
                    filter: {
                        type: "none",
                        value: 0
                    }
                }
            },
            tooltip: {
                style: {
                    fontSize: "12px",
                    fontFamily: KTAppSettings["font-family"]
                },
                y: {
                    formatter: function(t) {
                        return t + "%"
                    }
                }
            },
            colors: [KTAppSettings.colors.theme.light.info],
            grid: {
                borderColor: KTAppSettings.colors.gray["gray-200"],
                strokeDashArray: 4,
                yaxis: {
                    lines: {
                        show: !0
                    }
                }
            },
            markers: {
                strokeColor: KTAppSettings.colors.theme.base.info,
                strokeWidth: 3
            }
        };
        new ApexCharts(chat_time_element, chat_setting).render()
    }
}


$(document).ready(function(){
    console.log("popup.js");
    $("#clientName").on("change", function(){
        var clientName = $("#clientName").val();
        if(clientName == "test data"){
            init_chat(zero_data,zero_data);
            return;
        }
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            chrome.tabs.sendMessage(tabs[0].id, {action:"getData",clientName: clientName}, function(response){
                init_chat(response.data.active_time_arr, response.data.chat_time_arr);
                return true;
            });
        });
    });
    $("#init_data").on("click", function(){
        var clientName = $("#clientName").val();
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            chrome.tabs.sendMessage(tabs[0].id, {action:"initData",clientName: clientName},function(response){
                init_chat(zero_data, zero_data);
                return true;
            });
        });
    })
    chrome.extension.onMessage.addListener(listenPopup);
});

function listenPopup(request, sender, sendResponse) {
    if(request.action == "updateData"){
        init_chat(request.data.active_time_arr, request.data.chat_time_arr);
        sendResponse({ "success": true});
        return true;
    }
}

function get_client_name(){
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        chrome.tabs.sendMessage(tabs[0].id, {action:"getClientName"}, function(response){
            if(!response || response.url.indexOf("web.skype.com") == -1){
                $("body").html("This page is not allowed for extension");
                $("body").css("width","100px");
                $("body").css("height","50px");
                $("html").css("width","100px");
                $("html").css("height","50px");
                return;
            }
            $("#clientName").html("");
            if(Array.isArray(response.data)){
                $("#clientName").append("<option value='test data'>Test Data</option>");
                for (let i = 0; i < response.data.length; i++) {
                    var select_str = "<option value='" + response.data[i] + "'>" + response.data[i]; + "</option>";
                    $("#clientName").append(select_str);
                }
                return true;
            }
            else
                return false;
        });
    });
}
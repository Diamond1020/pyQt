chrome.extension.onMessage.addListener(onMessage);
function onMessage(request, sender, sendResponse) {
    if(request.action == "resetContext") {
      registerContextMenus(request.text);
      sendResponse({success: true});
    }
    if (request.action == 'getConfig') {
      sendResponse({data: {
        "enabled": localStorage['enabled'],
        "from": localStorage['from'],
        "to": localStorage['to'],
        "parse": localStorage['parse'],
        "dial": localStorage['dial'],
        "protocol": localStorage['protocol'],
        "theme": localStorage['theme'],
        "repintwith": localStorage['repintwith'],
        "repown": localStorage['repown'],
        "repownwith": localStorage['repownwith'],
        "custom-url": localStorage['custom-url'],
        "param1": localStorage['param1'],
        "param2": localStorage['param2'],
        "param3": localStorage['param3'],
        "param4": localStorage['param4'],
        "link-target": localStorage['link-target']
      }});
      return true;
    } 
  }
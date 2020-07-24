let button = document.getElementById('submitButton');
let log = document.getElementById('log');
let inputText = document.getElementById('inputText');
var loaded = false;
var submitting = false;   // Prevent submits during a submitting request

// Submit button listener
button.addEventListener('click', function() {
  if (!submitting) {
    submitting = true;
    botResponse();

    // Speech synthesis speaks if enabled and has content
    if (synthEnabled && speakcontent != "") {
      const utterThis = new SpeechSynthesisUtterance(speakcontent);
      synth.speak(utterThis);
      console.log("SPEAKING: "+speakcontent);
      speakcontent = "";
      notspoken = false;
    } else {
      console.log("NOT SPEAKING");
    }
  }
});

// Enter key listener
inputText.addEventListener('keyup', function(event) {
  // 13 = "Enter" key
  if (event.keyCode === 13 && !submitting) { 
    submitting = true;
    event.preventDefault();
    botResponse();

    // Speech synthesis speaks if enabled and has content
    if (synthEnabled && speakcontent != "") {
      const utterThis = new SpeechSynthesisUtterance(speakcontent);
      synth.speak(utterThis);
      console.log("SPEAKING: "+speakcontent);
      speakcontent = "";
      notspoken = false;
    } else {
      console.log("NOT SPEAKING");
    }
  }
});

// Opens a bot greeting
window.onload = botResponse;

function botResponse() {
  $("#submitButton").attr("disabled", true);
  if (loaded === false) {
    var inputTextVal = "usercmd:load";
  } else {
    var inputTextVal = inputText.value;
  }

  inputText.value = '';
  var htmlUser = '';
  var htmlBot = '';
  
  $.ajax("/get", {
    data: {inputText: inputTextVal},
    timeout: 50000,     //for debug
    async: false,       // Ensures the speech synthesis runs after this function
    //timeout: 5000     // Timeout 50 seconds (5000ms)
    success: function(outputTextVal) {
      // JSON result received
      try {
        // Is a JSON
        const chat_json = JSON.parse(outputTextVal);
        console.log("Chat JSON parsed")

        htmlUser = "";
        // Goes through the chat log given (only once if not a chat log)
        for (i in chat_json.chat_log) {
          if (chat_json.chat_log[i].type === 'user' && !(chat_json.chat_log[i].content === 'usercmd:load' && loaded === false)) {
            htmlBot += '<div class="userInputBox"><div><small>You: (' + chat_json.chat_log[i].datetime + ')</small><br>' + chat_json.chat_log[i].content + '</div></div>';
          } else if (chat_json.chat_log[i].type === 'bot') {
            htmlContent = chat_json.chat_log[i].content;
            htmlBot += '<div class="botInputBox"><div><small>Bot: (' + chat_json.chat_log[i].datetime + ')</small><br>' + htmlContent + '</div></div>';
            // Ensure the content is spoken if speech synthesis is enabled
            speakhasset = true;
            speakcontent = chat_json.chat_log[i].content;
            notspoken = true;
            console.log("set to speak: "+speakcontent)
          }
        }
        loaded = true;
      } catch (e) {
        console.log("not JSON or failed: "+e)
        // Not a JSON
        htmlBot = '<div class="botInputBox"><div><small>Bot: Error: </small><br>' + e + '</div></div>';
        loaded = true;
      }
    },
    error: function(xmlhttprequest, textstatus, message) {
      // Timeout reached or some request error
      htmlUser = '<div class="userInputBox"><div><small>You: Error: </small><br>' + inputTextVal + '</div></div>';
      if (textstatus === "timeout") {
        htmlBot =  '<div class="botInputBox"><div><small>Bot: Error: </small><br>Request timeout (taken too long, more than 5 seconds), request aborted.</div></div>';
      } else {
        htmlBot =  '<div class="botInputBox"><div><small>Bot: Error: </small><br>' + textstatus + '</div></div>';
      }
    },
    complete: function() {
      // Show the results on page
      log.innerHTML += htmlUser+htmlBot;
      log.scrollTop = log.scrollHeight;
      $("#submitButton").attr("disabled", false);
      submitting = false;
    }
  });
}

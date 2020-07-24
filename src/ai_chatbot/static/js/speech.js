/* Speech recognition script, only works (browser default settings) with Chrome/Chromium: uses SpeechRecognition
 * Firefox need to change setting in order to use it, only as experimental feature
 *
 * Part of the web API specification: https://wicg.github.io/speech-api/
 */

var inputTextBox = document.getElementById('inputText');
var voice_info = document.getElementById('voice_info');

var voiceButton = document.getElementById('voiceButton');
var voice_active = false;
 
try {
  var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  var recognition = new SpeechRecognition();

  recognition.continuous = true;    // Keeps on listening until it manually stopped
  recognition.lang = "en-GB";       // British accent

  voice_info.innerHTML = 'Click on \"Start recognition\" to start recording your voice!';
} catch (error) {
  // Unsupported browser
  console.log(error);
  voice_info.innerHTML = 'If you want to use speech recognition, use Chrome/Chromium instead. Firefox has experimental support.';
  voiceButton.hidden = true;
}

recognition.onend = function() {
  if (voice_active) {
    recognition.start();
  }
};

// Appends to the input box
recognition.onresult = function(event) {
  var current = event.resultIndex;
  var transcript = event.results[current][0].transcript;
  if (current > 0 || inputTextBox.value != '') {
    transcript = ' '+transcript;
  }
  inputTextBox.value += transcript;
};

// Button function to toggle voice recognition
voiceButton.addEventListener('click', function() {
  if (voice_active) {
    voice_active = false;
    recognition.stop();
    voice_info.innerHTML = 'Voice recognition stopped.';
    voiceButton.innerHTML = 'Start voice recognition';
  } else {
    voice_active = true;
    recognition.start();
    voice_info.innerHTML = 'Voice recognition is recording...';
    voiceButton.innerHTML = 'Stop voice recognition';
  }
});


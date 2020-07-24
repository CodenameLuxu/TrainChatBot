var synth = window.speechSynthesis;
var speakcontent = "";
var synthEnabled = false;
var speakhasset = false;
var ttsButton = document.getElementById('ttsButton');

ttsButton.addEventListener('click', function() {
  synthEnabled = !synthEnabled;
  if (synthEnabled) {
    ttsButton.innerHTML = "Disable text to speech";
  } else {
    ttsButton.innerHTML = "Enable text to speech";
  }
});


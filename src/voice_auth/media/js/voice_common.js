//this.REQUIRED_ARGS = ["monitorURL", "confirmURL", "cancelURL", "redirectURL", "fallbackURL"]
function BaseVoiceBlock (selector, applet, urls) {
    this.block = $(selector);
    this.urls = urls;
    this.applet = applet;
    this.is_applet_loaded = applet.isActive();

};

function recordAppletLoaded () {
    console.log("Applet loaded.");
    window.recorder = document.ListenUpRecorder;
    recorder.setUploadCompletionScript("uploadCompleted();");
    recorder.setUploadFailureScript("uploadFailed();");
    initialState(verificationBlock);
}



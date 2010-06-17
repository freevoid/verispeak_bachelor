function StateMachine (transitionTable) {
    this.transitionTable = transitionTable;

    // Main FSM function: search for action in transitionTable depending
    // on current state
    this.event = function (event_, args) {

        var actions = this.transitionTable[event_];
        if (typeof(actions) != "undefined") {
            var action = actions[this.state];
            if (typeof(action) != "undefined") {

                this[action].call(this, args);
            } else {

            }
        } else {

        }
    };
}

function BaseVoiceBlock (selector, params, urls, defer_creation) {

    if (typeof(selector) == "undefined") {
        return;
    }
    
    // CONSTANTS
    
    this.UPLOAD_COMPLETED_GLOBAL_NAME = "BaseVoiceBlock_uploadCompleted";
    this.UPLOAD_FAILED_GLOBAL_NAME = "BaseVoiceBlock_uploadFailed";
    

    var transitionTable = {
        created: {
            undefined: "to_created",
            applet_loaded: "to_initial"
        },
        applet_loaded: {
            undefined: "to_applet_loaded",
            created: "to_initial"
        },
        record: {
            initial: "to_recording",
            insufficient_to_upload: "to_recording"
        },
        pause: {recording: "to_pausing"},
        paused: {pausing: "to_paused"},

        stopped: {
            recording: "to_stopped",
            stopping: "to_stopped"
        },

        ready_to_upload: {paused: "to_uploading"},
        too_short_to_upload: {paused: "to_insufficient_to_upload"},
        upload_failed: {uploading: "to_upload_failed"},
        upload_completed: {uploading: "to_upload_completed"},
        cancel: {
            initial: "return_back",
            insufficient_to_upload: "return_back",
            failed_to_upload: "return_back"
        }
    };
    StateMachine.call(this, transitionTable);


    
    // PUT GLOBAL CALLBACKS

    this.uploadCompleted = function () {

        this_.event("upload_completed");
    };

    this.uploadFailed = function () {

        this_.event("upload_failed");
    };

    var this_ = this;
    this.appletReadyScript = function () {

        this_.applet = document[params.appletName];
        window[this_.UPLOAD_COMPLETED_GLOBAL_NAME] = this_.uploadCompleted;
        window[this_.UPLOAD_FAILED_GLOBAL_NAME] = this_.uploadFailed;
        this_.applet.setUploadCompletionScript(this_.UPLOAD_COMPLETED_GLOBAL_NAME + '();');
        this_.applet.setUploadFailureScript(this_.UPLOAD_FAILED_GLOBAL_NAME + '();');

        this_.applet.setAttribute("style", "width:1px;");
        this_.event("applet_loaded");
    };

    // handle applet state changing and call
    // appropriate callback method, if defined
    this.recordStateChanged = function (from, to) {

        var callback_name = "record_" + from + "_to_" + to;
        if (typeof(this_[callback_name]) != "undefined") {
            this_[callback_name].call(this_);
        }
    };

    // playing/record time update
    this.recordTimeChanged = function (current, max) {
        var timing = this_.getTimingBlock();
        if (timing) {
            timing.text(current.toFixed(2) + '/' + max.toFixed(2));
        }
    };
    
    window[params.recordTimeChangedScriptName] = this.recordTimeChanged;
    window[params.appletReadyScriptName] = this.appletReadyScript;
    window[params.recordStateChangedScriptName] = this.recordStateChanged;

    this.RECORD_BUTTON_SELECTOR = params.recordButtonId || "#id_record_button";
    this.CANCEL_BUTTON_SELECTOR = params.cancelButtonId || "#id_cancel_button";

    // ATTRIBUTES

    this.block = $(selector);
    this.urls = urls;
    this.uploadedCount = 0;
    this.uploadedTime = 0.0;
    this.timingBlockClass = params.timingBlockClass || "timingBlock";
    this.minLengthToUpload = params.minLengthToUpload || 1.5;
    this.appletName = params.appletName || "ListenUpRecorder";
    this.monitorDelay = params.monitorDelay || 2000; // 2 sec polling



    // BUTTONS CALLBACKS
    this.recordButtonClicked = function () {
        if (this_.applet.isRecording()) {
            this_.event("pause");
        } else {
            this_.event("record");
        }
    };

    this.cancelButtonClicked = function () {
        this_.event("cancel");
    };

    this.block.find(this.RECORD_BUTTON_SELECTOR).click(this.recordButtonClicked);
    this.block.find(this.CANCEL_BUTTON_SELECTOR).click(this.cancelButtonClicked);

    // Main condition to check if we can send data
    this.canSendToVerification = function () {
        return this.applet.isPlayable() && this.applet.getMaxPlayableTime() > this.minLengthToUpload;
    };

    this.record_recording_to_paused  = function () {
        this.event("paused");
    };

    this.record_recording_to_stopped = function () {
        this.event("stopped");
    };

    // Helper functions
    this.return_back = function (args) {
        window.location = this.urls.fallbackURL;
    };

    this.getTimingBlock = function () {
        var search_try = this.getContent().find('.' + this.timingBlockClass);
        if (search_try.length) {
            return search_try;
        } else {
            return null;
        }
    };

    this.getOrCreateTimingBlock = function () {
        var search_try = this.getTimingBlock();
        if (search_try !== null) {
            return search_try;
        } else {
            this.getContent().append('<span class="' + this.timingBlockClass +'"></span>');
            return this.getTimingBlock();
        }
    };

    this.setButtonEnabled = function(selector, is_enabled) {
        if (is_enabled) {
            this.block.find(selector).removeAttr("disabled");
        } else {
            this.block.find(selector).attr("disabled", "true");
        }
    };

    this.maskButtons = function(record_mask, cancel_mask) {
        this.setButtonEnabled(this.RECORD_BUTTON_SELECTOR, record_mask);
        this.setButtonEnabled(this.CANCEL_BUTTON_SELECTOR, cancel_mask);
    };

    this.getContent = function() {
        return this.block.find(".voice_auth_content");
    };

    this.clearContent = function() {
        this.getContent().html('');
    };

    this.pasteNote = function (note) {
        this.getContent().html('<span class="note">' + note + '</span>');
    };

    this.pasteError = function (note) {
        this.getContent().html('<span class="errornote">' + note + '</span>');
    };

    this.setLoading = function(message) {
        this.getContent().html(
            '<img src="/media/img/loading.gif" id="id_loading_img" /><span class="loadingMessage">' + message + '</span><span class="' + this.timingBlockClass + '"></span>');
    };

    this.sessionContext = function() {
        return this.block.find("form").serializeArray();
    };

    this.sessionId = function() {
        return this.block.find("form input[name=session_id]").val();
    };

    if (!defer_creation) {
        this.event("created");
    }
}

// Default state transitions
BaseVoiceBlock.method('to_created', function (args) {
    this.state = "created";
    this.setLoading("Ожидается загрузка апплета..");
    this.maskButtons(false, true);
});

BaseVoiceBlock.method('to_applet_loaded', function (args) {
    this.state = "applet_loaded";
    this.setLoading("Апплет загружен, завершение инициализации..");
    this.maskButtons(false, true);
});

BaseVoiceBlock.method('to_initial', function (args) {
    this.state = "initial";
    this.pasteNote("Нажмите кнопку &laquo;Запись&raquo;, произнесите ключевую фразу, и нажмите на кнопку &laquo;Стоп&raquo;.");
    this.maskButtons(true, true);
});

BaseVoiceBlock.method('to_recording', function (args) {
    this.state = "recording";
    this.setLoading("Идёт запись..");
    this.block.find(this.RECORD_BUTTON_SELECTOR).val("Стоп");
    this.maskButtons(true, false);
    this.applet.record();
});

BaseVoiceBlock.method('to_pausing', function (args) {
    this.state = "pausing";
    this.applet.pauseAudio();
});

BaseVoiceBlock.method('to_uploading', function (args) {
    this.state = "uploading";
    this.currentUploadingTime = this.applet.getMaxPlayableTime();
    this.maskButtons(false, false);
    this.setLoading("Запись отправляется на сервер..");
    this.applet.stopAudio();

    this.applet.addNameValuePair("session_id", this.sessionId());
    this.applet.sendRecordedMessage();
});

BaseVoiceBlock.method('to_paused', function (args) {
    this.state = "paused";
    this.block.find(this.RECORD_BUTTON_SELECTOR).val("Запись");

    if (this.canSendToVerification()) {
        this.event("ready_to_upload");
    } else {
        this.event("too_short_to_upload",
                {recorded_time: this.applet.getMaxPlayableTime()}
        );
    }
});

BaseVoiceBlock.method('to_stopped', function (args) {
    // assuming that to_paused will emit ready_to_upload
    // because if it don't then recorded message will be lost
    this.to_paused(args);
});

BaseVoiceBlock.method('to_insufficient_to_upload', function (args) {
    this.state = "insufficient_to_upload";
    this.pasteNote(sprintf('Записан слишком короткий образец (%.2f сек.). Повторите запись ещё раз.',
                args.recorded_time));
    this.maskButtons(true, true);
});

BaseVoiceBlock.method('to_upload_failed', function (args) {
    this.state = "upload_failed";
    this.pasteError("Ошибка при отправке записи на сервер. Попробуйте ещё раз или обратитесь в службу поддержки.");
    this.maskButtons(false, true);
});

BaseVoiceBlock.method("to_upload_completed", function (args) {
    this.state = "upload_completed";
    this.pasteNote("Запись отправлена.");
    this.maskButtons(true, true);
    this.uploadedCount += 1;
    this.uploadedTime += this.currentUploadingTime;
    this.currentUploadingTime = undefined;
});


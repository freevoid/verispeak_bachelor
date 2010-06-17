function UploadingBlock (selector, params, urls) {
    BaseVoiceBlock.call(this, selector, params, urls, true);

    // Attributes
    this.minUploadedCount = params.minUploadedCount || 3;
    this.minUploadedTime = params.minUploadedTime || 5.0;

    this_ = this;
    this.CONFIRM_BUTTON_SELECTOR = params.confirmButtonId || "#id_confirm_button";
    this.confirmButtonClicked = function () {
        this_.event("confirm");
    };
    $(this.CONFIRM_BUTTON_SELECTOR).click(this.confirmButtonClicked);

    this.transitionTable["cancel"] = {
        initial: "return_back",
        failed: "return_back",
        error_in_learning: "return_back",
        learning: "interrupted",
        interrupted: "return_back",
        failed_to_upload: "return_back",
        upload_completed: "cancel_registration",
        insufficient_to_upload: "cancel_registration",
        insufficient_to_enroll: "cancel_registration"
    };

    this.transitionTable["record"] = {
        initial: "to_recording",
        insufficient_to_upload: "to_recording",
        upload_completed: "record_another_one",
        insufficient_to_enroll: "record_another_one"
    };

    this.transitionTable["confirm"] = {
        upload_completed: "to_confirmed"
    };

    this.transitionTable["learning_started"] = {
        confirmed: "to_learning"
    };

    this.transitionTable["error_in_learning"] = {
        learning: "to_error_in_learning"
    };
    
    this.transitionTable["learning_success"] = {
        learning: "to_learning_success"
    };

    this.transitionTable["insufficient_to_enroll"] = {
        learning: "to_insufficient_to_enroll"
    };

    this.maskButtons = function (record_mask, cancel_mask, confirm_mask) {
        this.setButtonEnabled(this.RECORD_BUTTON_SELECTOR, record_mask);
        this.setButtonEnabled(this.CANCEL_BUTTON_SELECTOR, cancel_mask);
        this.setButtonEnabled(this.CONFIRM_BUTTON_SELECTOR, confirm_mask);
    };

    var this_ = this;
    this.monitorProgress = function() {

        $.ajax({
            type: 'GET',
            url: this_.urls.monitorURL,
            data: this_.sessionContext(),
            success: function (data) {


                var code = data.result;
                if (code == 0) {
                    var state = data.message;
                    if (state == "finished") {

                        this_.event("learning_success");
                    } else if (state == "waiting_for_data") {
                        this_.event("insufficient_to_enroll");
                    } else if (state == "failed") {
                        this_.event("error_in_learning", {description: "В процессе обучения произошла ошибка"});
                    } else if (state == "interrupted") {
                        this_.event("cancel");
                    } else {
                        setTimeout(this_.monitorProgress, this_.monitorDelay);
                    }
                } else {
                    alert("Необработанный ответ:", code, data.message);
                    setTimeout(this_.monitorProgress, this_.monitorDelay);
                }
            },
            error: function (data) {

                setTimeout(this_.monitorProgress, this_.monitorDelay);
            },
            dataType: "json"
        });
    };

    this.updateUploadedTiming = function () {
        var target = this.getPreContent();
        target.text("Загружено: " + this.uploadedCount +
                "; Общая длительность: " + this.uploadedTime.toFixed(2) + "сек.");
    };

    this.readyToEnroll = function () {
        return (this.uploadedCount > this.minUploadedCount)
            && (this.uploadedTime > this.minUploadedTime);
    };

    this.getContent().before('<div class="pre_content"></div>');
    this.getPreContent = function() {
        return this.block.find(".pre_content");
    };

    this.event("created");
}

UploadingBlock.inherits(BaseVoiceBlock);

UploadingBlock.method('to_upload_completed', function (args) {
    this.uber('to_upload_completed');
    this.maskButtons(true, true, true);
});

UploadingBlock.method('cancel_registration', function (args) {

    this_ = this;
    $.post(this.urls.cancelURL, this.sessionContext(),
            function (data) {
                if (data.result == 0) {
                    window.location = this_.urls.fallbackURL;
                } else {
                    alert(data.message);
                }
            }, "json");
});

UploadingBlock.method('to_confirmed', function (args) {
    this_ = this;
    $.ajax({
        type: 'POST',
        url: this.urls.confirmURL,
        data: this.sessionContext(),
        success: function (data) {
            if (data.result == 0) {
                this_.state = "confirmed";
                this_.event("learning_started");
            } else {
                alert(data.message);
            }
        },
        error: function (data) {
            alert("Произошла ошибка при отправке запроса на сервер." +
                "Попытайтесь снова или обратитесь в службу поддержки.");
        },
        dataType: "json"
    });
});

UploadingBlock.method('to_learning', function (args) {
    this.state = "learning";
    this.setLoading("Подождите, идёт процесс обучения модели..");
    this.maskButtons(false, false);
    this.monitorProgress();
});

UploadingBlock.method('to_error_in_learning', function (args) {
    this.state = "error_in_learning";
    this.pasteError(args.description +
            '. Попробуйте ещё раз. Если ошибка возникает снова, обратитесь в службу поддержки.');
    this.maskButtons(false, true);
});

UploadingBlock.method('to_insufficient_to_enroll', function (args) {
    this.state = "insufficient_to_enroll";
    this.pasteError("Обучение завершилось неудачно. Попробуйте ещё раз, загрузив больше голосовых данных.");
    this.maskButtons(true, true);
});

UploadingBlock.method('to_learning_success', function (args) {
    this.state = "learning_success";
    this.getPreContent().remove();
    this.pasteNote("Вы успешно зарегистрированы в системе голосовой аутентификации!" +
        " Переход будет выполнен автоматически..");

    var this_ = this;
    setTimeout(function() { window.location = this_.urls.redirectURL }, 2000);
    this.maskButtons(false, false);
});

UploadingBlock.method('record_another_one', function (args) {
    this.applet.erase();
    this.uber("to_recording");
});

UploadingBlock.method('to_upload_completed', function() {
    this.uber('to_upload_completed');
    if (this.readyToEnroll()) {
        this.maskButtons(true, true, true); // enable "confirm" button
    };
    this.updateUploadedTiming();
});

UploadingBlock.method('interrupted', function () {
    this.state = 'interrupted';
    this.pasteError("Процесс обучения был прерван на стороне сервера.");
    this.maskButtons(false, true);
});


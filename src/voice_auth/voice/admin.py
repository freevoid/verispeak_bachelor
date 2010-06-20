from django.contrib import admin

from django.utils.translation import ugettext_lazy as _

from models import *

class UtteranceInline(admin.StackedInline):
    model = UploadedUtterance

class UploadedUtteranceAdmin(admin.ModelAdmin):
    list_display = ('id', 'uploaded_date', 'utterance_file', 'is_trash')
    date_hierarchy = 'uploaded_date'
    list_filter = ('is_trash',)

class RecordSessionAdmin(admin.ModelAdmin):
    actions = ['delete_ghost_sessions']
    inlines = [UtteranceInline]
    date_hierarchy = 'created_time'
    list_display = ('id', 'created_time', 'target_speaker', 'utterance_count', 'authentic')
    list_filter = ('authentic', 'target_speaker')

    def delete_ghost_sessions(self, request, queryset):
        queryset.filter(uploadedutterance__isnull=True).delete()

class SpeakerModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'speaker', 'is_active', 'model_file')
    list_filter = ('speaker', 'is_active')

    actions = ['set_active']
    def set_active(self, request, queryset):
        try:
            model = queryset.get()
        except:
            pass
        else:
            model.active_prop = True
    set_active.short_description = _('Set selected model active')

class VerificationProcessAdmin(admin.ModelAdmin):
    list_display = ('id', 'state_id', 'verification_result', 'verification_score', 'target_session')
    list_filter = ('state_id', 'verification_result')
    date_hierarchy = 'start_time'

class LearningProcessAdmin(admin.ModelAdmin):
    list_display = ('id', 'state_id',  'start_time', 'finish_time', 'sample_sessions_count', 'result_model')
    list_filter = ('state_id',)
    date_hierarchy = 'start_time'

    actions = ['set_active']
    def set_active(self, request, queryset):
        try:
            process = queryset.get()
        except:
            pass
        else:
            if process.result_model is not None:
                process.result_model.active_prop = True
    set_active.short_description = _('Set active state to model created by selected process')

class RecordSessionMetaAdmin(admin.ModelAdmin):
    list_filter = ('gender',)
    list_display = ('id', 'record_session', 'gender', 'prompt', 'description')

class LLRVerificatorAdmin(admin.ModelAdmin):
    list_display = ('id', 'treshhold', 'null_estimator', 'alternative_estimator')
    list_filter = ('alternative_estimator',)

admin.site.register(UploadedUtterance, UploadedUtteranceAdmin)
admin.site.register(RecordSessionMeta, RecordSessionMetaAdmin)
admin.site.register(RecordSession, RecordSessionAdmin)
admin.site.register(VerificationProcess, VerificationProcessAdmin)
admin.site.register(UniversalBackgroundModel)
admin.site.register(LearningProcess, LearningProcessAdmin)
admin.site.register(LLRVerificator, LLRVerificatorAdmin)
admin.site.register(SpeakerModel, SpeakerModelAdmin)


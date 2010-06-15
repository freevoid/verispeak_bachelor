from django.contrib import admin

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
    list_display = ('id', 'speaker', 'learning_process', 'is_active', 'model_file')
    list_filter = ('speaker', 'is_active')

class VerificationProcessAdmin(admin.ModelAdmin):
    list_display = ('id', 'state_id', 'verification_result', 'verification_score', 'target_session')
    list_filter = ('state_id', 'verification_result')
    date_hierarchy = 'start_time'

class LearningProcessAdmin(admin.ModelAdmin):
    list_display = ('id', 'state_id',  'start_time', 'finish_time', 'sample_sessions_count')
    list_filter = ('state_id',)
    date_hierarchy = 'start_time'

class RecordSessionMetaAdmin(admin.ModelAdmin):
    list_filter = ('gender',)
    list_display = ('id', 'record_session', 'gender', 'prompt')

admin.site.register(UploadedUtterance, UploadedUtteranceAdmin)
admin.site.register(RecordSessionMeta, RecordSessionMetaAdmin)
admin.site.register(RecordSession, RecordSessionAdmin)
admin.site.register(VerificationProcess, VerificationProcessAdmin)
admin.site.register(UniversalBackgroundModel)
admin.site.register(LearningProcess, LearningProcessAdmin)
admin.site.register(LLRVerificator)
admin.site.register(SpeakerModel, SpeakerModelAdmin)


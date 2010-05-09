from django.contrib import admin

from models import *

admin.site.register(UploadedUtterance)
admin.site.register(RecordSession)
admin.site.register(VerificationSession)
admin.site.register(VerificationProcess)
admin.site.register(LearningProcess)


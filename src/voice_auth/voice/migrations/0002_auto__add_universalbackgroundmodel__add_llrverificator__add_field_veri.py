# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'UniversalBackgroundModel'
        db.create_table('voice_universalbackgroundmodel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('model_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('voice', ['UniversalBackgroundModel'])

        # Adding model 'LLRVerificator'
        db.create_table('voice_llrverificator', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('treshhold', self.gf('django.db.models.fields.FloatField')()),
            ('null_estimator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['voice.SpeakerModel'])),
            ('alternative_estimator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['voice.UniversalBackgroundModel'])),
        ))
        db.send_create_signal('voice', ['LLRVerificator'])

        # Adding field 'VerificationProcess.verification_score'
        db.add_column('voice_verificationprocess', 'verification_score', self.gf('django.db.models.fields.FloatField')(null=True, blank=True), keep_default=False)

        # Changing field 'VerificationProcess.verificated_by'
        db.alter_column('voice_verificationprocess', 'verificated_by_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['voice.LLRVerificator'], null=True, blank=True))

        # Adding field 'UploadedUtterance.is_trash'
        db.add_column('voice_uploadedutterance', 'is_trash', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True), keep_default=False)

        # Adding field 'RecordSession.authentic'
        db.add_column('voice_recordsession', 'authentic', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting model 'UniversalBackgroundModel'
        db.delete_table('voice_universalbackgroundmodel')

        # Deleting model 'LLRVerificator'
        db.delete_table('voice_llrverificator')

        # Deleting field 'VerificationProcess.verification_score'
        db.delete_column('voice_verificationprocess', 'verification_score')

        # Changing field 'VerificationProcess.verificated_by'
        db.alter_column('voice_verificationprocess', 'verificated_by_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['voice.SpeakerModel'], null=True, blank=True))

        # Deleting field 'UploadedUtterance.is_trash'
        db.delete_column('voice_uploadedutterance', 'is_trash')

        # Deleting field 'RecordSession.authentic'
        db.delete_column('voice_recordsession', 'authentic')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'voice.learningprocess': {
            'Meta': {'object_name': 'LearningProcess'},
            'finish_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sample_sessions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['voice.RecordSession']", 'symmetrical': 'False'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'state_id': ('django.db.models.fields.CharField', [], {'max_length': '24'})
        },
        'voice.llrverificator': {
            'Meta': {'object_name': 'LLRVerificator'},
            'alternative_estimator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['voice.UniversalBackgroundModel']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'null_estimator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['voice.SpeakerModel']"}),
            'treshhold': ('django.db.models.fields.FloatField', [], {})
        },
        'voice.recordsession': {
            'Meta': {'object_name': 'RecordSession'},
            'authentic': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'remote_ip': ('django.db.models.fields.IntegerField', [], {}),
            'session_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'target_speaker': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'})
        },
        'voice.speaker': {
            'Meta': {'object_name': 'Speaker', 'db_table': "'auth_user'", '_ormbases': ['auth.User']}
        },
        'voice.speakermodel': {
            'Meta': {'object_name': 'SpeakerModel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'learning_process': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['voice.LearningProcess']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'model_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'speaker': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'voice.universalbackgroundmodel': {
            'Meta': {'object_name': 'UniversalBackgroundModel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        'voice.uploadedutterance': {
            'Meta': {'object_name': 'UploadedUtterance'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_trash': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['voice.RecordSession']"}),
            'uploaded_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'utterance_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        'voice.verificationprocess': {
            'Meta': {'object_name': 'VerificationProcess'},
            'finish_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'state_id': ('django.db.models.fields.CharField', [], {'max_length': '24'}),
            'target_session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['voice.RecordSession']"}),
            'verificated_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['voice.LLRVerificator']", 'null': 'True', 'blank': 'True'}),
            'verification_result': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'verification_score': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['voice']

# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'RecordSession'
        db.create_table('voice_recordsession', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('session_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=32)),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('target_speaker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('authentic', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('remote_ip', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('voice', ['RecordSession'])

        # Adding model 'LearningProcess'
        db.create_table('voice_learningprocess', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('state_id', self.gf('django.db.models.fields.CharField')(max_length=24)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('finish_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('voice', ['LearningProcess'])

        # Adding M2M table for field sample_sessions on 'LearningProcess'
        db.create_table('voice_learningprocess_sample_sessions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('learningprocess', models.ForeignKey(orm['voice.learningprocess'], null=False)),
            ('recordsession', models.ForeignKey(orm['voice.recordsession'], null=False))
        ))
        db.create_unique('voice_learningprocess_sample_sessions', ['learningprocess_id', 'recordsession_id'])

        # Adding model 'SpeakerModel'
        db.create_table('voice_speakermodel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('model_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('speaker', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('learning_process', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['voice.LearningProcess'], unique=True, null=True, blank=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
        ))
        db.send_create_signal('voice', ['SpeakerModel'])

        # Adding model 'UniversalBackgroundModel'
        db.create_table('voice_universalbackgroundmodel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('model_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('voice', ['UniversalBackgroundModel'])

        # Adding model 'UploadedUtterance'
        db.create_table('voice_uploadedutterance', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('utterance_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('uploaded_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('is_trash', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('session', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['voice.RecordSession'])),
        ))
        db.send_create_signal('voice', ['UploadedUtterance'])

        # Adding model 'LLRVerificator'
        db.create_table('voice_llrverificator', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('treshhold', self.gf('django.db.models.fields.FloatField')()),
            ('null_estimator', self.gf('django.db.models.fields.related.OneToOneField')(related_name='llr_verificator', unique=True, to=orm['voice.SpeakerModel'])),
            ('alternative_estimator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['voice.UniversalBackgroundModel'], blank=True)),
        ))
        db.send_create_signal('voice', ['LLRVerificator'])

        # Adding model 'VerificationProcess'
        db.create_table('voice_verificationprocess', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('state_id', self.gf('django.db.models.fields.CharField')(max_length=24)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('target_session', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['voice.RecordSession'])),
            ('finish_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('verification_result', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('verification_score', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('verificated_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['voice.LLRVerificator'], null=True, blank=True)),
        ))
        db.send_create_signal('voice', ['VerificationProcess'])

        # Adding model 'RecordSessionMeta'
        db.create_table('voice_recordsessionmeta', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('record_session', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['voice.RecordSession'], unique=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(default='M', max_length=1)),
            ('prompt', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
        ))
        db.send_create_signal('voice', ['RecordSessionMeta'])


    def backwards(self, orm):
        
        # Deleting model 'RecordSession'
        db.delete_table('voice_recordsession')

        # Deleting model 'LearningProcess'
        db.delete_table('voice_learningprocess')

        # Removing M2M table for field sample_sessions on 'LearningProcess'
        db.delete_table('voice_learningprocess_sample_sessions')

        # Deleting model 'SpeakerModel'
        db.delete_table('voice_speakermodel')

        # Deleting model 'UniversalBackgroundModel'
        db.delete_table('voice_universalbackgroundmodel')

        # Deleting model 'UploadedUtterance'
        db.delete_table('voice_uploadedutterance')

        # Deleting model 'LLRVerificator'
        db.delete_table('voice_llrverificator')

        # Deleting model 'VerificationProcess'
        db.delete_table('voice_verificationprocess')

        # Deleting model 'RecordSessionMeta'
        db.delete_table('voice_recordsessionmeta')


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
            'alternative_estimator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['voice.UniversalBackgroundModel']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'null_estimator': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'llr_verificator'", 'unique': 'True', 'to': "orm['voice.SpeakerModel']"}),
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
        'voice.recordsessionmeta': {
            'Meta': {'object_name': 'RecordSessionMeta'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'default': "'M'", 'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'prompt': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'record_session': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['voice.RecordSession']", 'unique': 'True'})
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
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
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

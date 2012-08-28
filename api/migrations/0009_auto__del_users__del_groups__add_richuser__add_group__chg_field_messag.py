# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Users'
        db.delete_table('api_users')

        # Deleting model 'Groups'
        db.delete_table('api_groups')

        # Removing M2M table for field users on 'Groups'
        db.delete_table('api_groups_users')

        # Adding model 'RichUser'
        db.create_table('api_richuser', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('university', self.gf('django.db.models.fields.CharField')(max_length=32, null=True)),
            ('phone_number', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('preferred_contact_method', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal('api', ['RichUser'])

        # Adding model 'Group'
        db.create_table('api_group', (
            ('group_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('group_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('api', ['Group'])

        # Adding M2M table for field users on 'Group'
        db.create_table('api_group_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('group', models.ForeignKey(orm['api.group'], null=False)),
            ('richuser', models.ForeignKey(orm['api.richuser'], null=False))
        ))
        db.create_unique('api_group_users', ['group_id', 'richuser_id'])


        # Changing field 'MessageThread.group'
        db.alter_column('api_messagethread', 'group_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.Group']))

        # Changing field 'PinnedItem.group'
        db.alter_column('api_pinneditem', 'group_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.Group']))

    def backwards(self, orm):
        # Adding model 'Users'
        db.create_table('api_users', (
            ('phone_number', self.gf('django.db.models.fields.IntegerField')()),
            ('university', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('preferred_contact_method', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('api', ['Users'])

        # Adding model 'Groups'
        db.create_table('api_groups', (
            ('group_name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('group_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('api', ['Groups'])

        # Adding M2M table for field users on 'Groups'
        db.create_table('api_groups_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('groups', models.ForeignKey(orm['api.groups'], null=False)),
            ('users', models.ForeignKey(orm['api.users'], null=False))
        ))
        db.create_unique('api_groups_users', ['groups_id', 'users_id'])

        # Deleting model 'RichUser'
        db.delete_table('api_richuser')

        # Deleting model 'Group'
        db.delete_table('api_group')

        # Removing M2M table for field users on 'Group'
        db.delete_table('api_group_users')


        # Changing field 'MessageThread.group'
        db.alter_column('api_messagethread', 'group_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.Groups']))

        # Changing field 'PinnedItem.group'
        db.alter_column('api_pinneditem', 'group_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.Groups']))

    models = {
        'api.group': {
            'Meta': {'object_name': 'Group'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'group_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'group_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'group_set'", 'symmetrical': 'False', 'to': "orm['api.RichUser']"})
        },
        'api.message': {
            'Meta': {'object_name': 'Message'},
            'author_id': ('django.db.models.fields.IntegerField', [], {}),
            'author_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sent': ('django.db.models.fields.DateTimeField', [], {}),
            'snippet': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'thread': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['api.MessageThread']"})
        },
        'api.messagethread': {
            'Meta': {'object_name': 'MessageThread'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['api.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subject': ('django.db.models.fields.TextField', [], {})
        },
        'api.pinneditem': {
            'Meta': {'object_name': 'PinnedItem'},
            'author_id': ('django.db.models.fields.IntegerField', [], {}),
            'author_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'caption': ('django.db.models.fields.TextField', [], {}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['api.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        'api.richuser': {
            'Meta': {'object_name': 'RichUser'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone_number': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'preferred_contact_method': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'university': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['api']
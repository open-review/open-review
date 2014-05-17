# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Review.timestamp'
        db.alter_column('main_review', 'timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))
        # Adding index on 'Author', fields ['name']
        db.create_index('main_author', ['name'])

        # Adding unique constraint on 'Author', fields ['name']
        db.create_unique('main_author', ['name'])

        # Adding index on 'Keyword', fields ['label']
        db.create_index('main_keyword', ['label'])


    def backwards(self, orm):
        # Removing index on 'Keyword', fields ['label']
        db.delete_index('main_keyword', ['label'])

        # Removing unique constraint on 'Author', fields ['name']
        db.delete_unique('main_author', ['name'])

        # Removing index on 'Author', fields ['name']
        db.delete_index('main_author', ['name'])


        # Changing field 'Review.timestamp'
        db.alter_column('main_review', 'timestamp', self.gf('django.db.models.fields.DateTimeField')())

    models = {
        'accounts.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'blank': 'True', 'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '30'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'to': "orm['auth.Group']", 'symmetrical': 'False', 'related_name': "'user_set'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'to': "orm['auth.Permission']", 'symmetrical': 'False', 'related_name': "'user_set'"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'to': "orm['auth.Permission']", 'symmetrical': 'False'})
        },
        'auth.permission': {
            'Meta': {'object_name': 'Permission', 'unique_together': "(('content_type', 'codename'),)", 'ordering': "('content_type__app_label', 'content_type__model', 'codename')"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'contenttypes.contenttype': {
            'Meta': {'db_table': "'django_content_type'", 'object_name': 'ContentType', 'unique_together': "(('app_label', 'model'),)", 'ordering': "('name',)"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'main.author': {
            'Meta': {'object_name': 'Author'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'db_index': 'True', 'unique': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['accounts.User']"})
        },
        'main.keyword': {
            'Meta': {'object_name': 'Keyword'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.TextField', [], {'db_index': 'True'})
        },
        'main.paper': {
            'Meta': {'object_name': 'Paper'},
            'abstract': ('django.db.models.fields.TextField', [], {}),
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.Author']", 'symmetrical': 'False'}),
            'doc_id': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.Keyword']", 'symmetrical': 'False'}),
            'publish_date': ('django.db.models.fields.DateField', [], {'blank': 'True', 'null': 'True'}),
            'publisher': ('django.db.models.fields.TextField', [], {'blank': 'True', 'null': 'True'}),
            'title': ('django.db.models.fields.TextField', [], {}),
            'urls': ('django.db.models.fields.TextField', [], {'blank': 'True', 'null': 'True'})
        },
        'main.review': {
            'Meta': {'object_name': 'Review'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'paper': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Paper']", 'related_name': "'reviews'"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['main.Review']"}),
            'poster': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.User']"}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'})
        },
        'main.vote': {
            'Meta': {'object_name': 'Vote'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'review': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Review']"}),
            'vote': ('django.db.models.fields.SmallIntegerField', [], {}),
            'voter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.User']"})
        }
    }

    complete_apps = ['main']

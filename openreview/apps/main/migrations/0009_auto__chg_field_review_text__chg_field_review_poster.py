# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Review.text'
        db.alter_column('main_review', 'text', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Review.poster'
        db.alter_column('main_review', 'poster_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.User'], null=True))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Review.text'
        raise RuntimeError("Cannot reverse this migration. 'Review.text' and its values cannot be restored.")

        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Review.text'
        db.alter_column('main_review', 'text', self.gf('django.db.models.fields.TextField')())

        # User chose to not deal with backwards NULL issues for 'Review.poster'
        raise RuntimeError("Cannot reverse this migration. 'Review.poster' and its values cannot be restored.")

        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Review.poster'
        db.alter_column('main_review', 'poster_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.User']))

    models = {
        'accounts.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'related_name': "'user_set'", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'related_name': "'user_set'", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'ordering': "('name',)", 'db_table': "'django_content_type'", 'object_name': 'ContentType'},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'main.author': {
            'Meta': {'object_name': 'Author'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'unique': 'True', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.User']", 'null': 'True'})
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
            'publish_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'publisher': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.TextField', [], {}),
            'urls': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'main.review': {
            'Meta': {'object_name': 'Review'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'paper': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Paper']", 'related_name': "'reviews'"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Review']", 'null': 'True'}),
            'poster': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.User']", 'null': 'True'}),
            'rating': ('django.db.models.fields.SmallIntegerField', [], {'default': '-1'}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'main.vote': {
            'Meta': {'unique_together': "(('review', 'voter'),)", 'object_name': 'Vote'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'review': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Review']", 'related_name': "'votes'"}),
            'vote': ('django.db.models.fields.SmallIntegerField', [], {'db_index': 'True'}),
            'voter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.User']", 'related_name': "'votes'"})
        }
    }

    complete_apps = ['main']

# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Review'
        db.create_table('main_review', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')()),
            ('poster', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.User'])),
            ('paper', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Paper'], related_name='reviews')),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Review'], null=True)),
        ))
        db.send_create_signal('main', ['Review'])

        # Adding model 'Vote'
        db.create_table('main_vote', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vote', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('review', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Review'])),
            ('voter', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.User'])),
        ))
        db.send_create_signal('main', ['Vote'])

        # Adding model 'Keyword'
        db.create_table('main_keyword', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('main', ['Keyword'])

        # Adding model 'Author'
        db.create_table('main_author', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['accounts.User'], null=True)),
            ('name', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('main', ['Author'])

        # Adding model 'Paper'
        db.create_table('main_paper', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('doc_id', self.gf('django.db.models.fields.TextField')()),
            ('title', self.gf('django.db.models.fields.TextField')()),
            ('abstract', self.gf('django.db.models.fields.TextField')()),
            ('publisher', self.gf('django.db.models.fields.TextField')()),
            ('publish_date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('main', ['Paper'])

        # Adding M2M table for field authors on 'Paper'
        m2m_table_name = db.shorten_name('main_paper_authors')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('paper', models.ForeignKey(orm['main.paper'], null=False)),
            ('author', models.ForeignKey(orm['main.author'], null=False))
        ))
        db.create_unique(m2m_table_name, ['paper_id', 'author_id'])

        # Adding M2M table for field keywords on 'Paper'
        m2m_table_name = db.shorten_name('main_paper_keywords')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('paper', models.ForeignKey(orm['main.paper'], null=False)),
            ('keyword', models.ForeignKey(orm['main.keyword'], null=False))
        ))
        db.create_unique(m2m_table_name, ['paper_id', 'keyword_id'])


    def backwards(self, orm):
        # Deleting model 'Review'
        db.delete_table('main_review')

        # Deleting model 'Vote'
        db.delete_table('main_vote')

        # Deleting model 'Keyword'
        db.delete_table('main_keyword')

        # Deleting model 'Author'
        db.delete_table('main_author')

        # Deleting model 'Paper'
        db.delete_table('main_paper')

        # Removing M2M table for field authors on 'Paper'
        db.delete_table(db.shorten_name('main_paper_authors'))

        # Removing M2M table for field keywords on 'Paper'
        db.delete_table(db.shorten_name('main_paper_keywords'))


    models = {
        'accounts.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'blank': 'True', 'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '30'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True', 'symmetrical': 'False', 'related_name': "'user_set'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True', 'symmetrical': 'False', 'related_name': "'user_set'"}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True', 'symmetrical': 'False'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'contenttypes.contenttype': {
            'Meta': {'db_table': "'django_content_type'", 'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType'},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'main.author': {
            'Meta': {'object_name': 'Author'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.User']", 'null': 'True'})
        },
        'main.keyword': {
            'Meta': {'object_name': 'Keyword'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.TextField', [], {})
        },
        'main.paper': {
            'Meta': {'object_name': 'Paper'},
            'abstract': ('django.db.models.fields.TextField', [], {}),
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.Author']", 'symmetrical': 'False'}),
            'doc_id': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['main.Keyword']", 'symmetrical': 'False'}),
            'publish_date': ('django.db.models.fields.DateField', [], {}),
            'publisher': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.TextField', [], {})
        },
        'main.review': {
            'Meta': {'object_name': 'Review'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'paper': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Paper']", 'related_name': "'reviews'"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Review']", 'null': 'True'}),
            'poster': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['accounts.User']"}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {})
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

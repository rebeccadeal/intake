# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-08-27 02:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('intake', '0021_tie_orgs_to_submissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='FilledPDF',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pdf', models.FileField(upload_to='filled_pdfs/')),
                ('original_pdf', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='filled_copies', to='intake.FillablePDF')),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='filled_pdfs', to='intake.FormSubmission')),
            ],
        ),
    ]

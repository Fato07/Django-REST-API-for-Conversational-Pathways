# Generated by Django 5.1.1 on 2024-10-03 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agents', '0008_alter_agent_bland_ai_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='webhook',
            field=models.URLField(blank=True, null=True),
        ),
    ]

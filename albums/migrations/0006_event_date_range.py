from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('albums', '0005_document_title_optional'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='date',
            new_name='start_date',
        ),
        migrations.AddField(
            model_name='event',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]

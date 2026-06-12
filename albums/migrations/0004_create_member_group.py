from django.db import migrations

MEMBER_GROUP = '系學會會員'


def create_member_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name=MEMBER_GROUP)


def remove_member_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name=MEMBER_GROUP).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('albums', '0003_add_eventdocument'),
    ]

    operations = [
        migrations.RunPython(create_member_group, remove_member_group),
    ]

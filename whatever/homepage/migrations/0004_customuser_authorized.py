from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0003_customuser_class_designation'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='authorized',
            field=models.BooleanField(
                default=False,
                help_text='Whether this account is authorized to use teacher features',
            ),
        ),
    ]
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studentside', '0003_proctoringsessionfiles'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentexamattempt',
            name='prediction_artifact',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='studentexamattempt',
            name='prediction_completed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='studentexamattempt',
            name='prediction_confidence',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='studentexamattempt',
            name='prediction_error',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='studentexamattempt',
            name='prediction_label',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='studentexamattempt',
            name='prediction_model_version',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='studentexamattempt',
            name='prediction_status',
            field=models.CharField(default='pending', max_length=20),
        ),
        migrations.AddField(
            model_name='studentexamattempt',
            name='probability_cheating',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='studentexamattempt',
            name='probability_non_cheating',
            field=models.FloatField(blank=True, null=True),
        ),
    ]

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE INDEX idx_notification_log_statut ON iltizam_notification_logs(statut);",
            reverse_sql="DROP INDEX idx_notification_log_statut ON iltizam_notification_logs;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_notification_log_date ON iltizam_notification_logs(date_envoi);",
            reverse_sql="DROP INDEX idx_notification_log_date ON iltizam_notification_logs;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_notification_log_type ON iltizam_notification_logs(type_notification);",
            reverse_sql="DROP INDEX idx_notification_log_type ON iltizam_notification_logs;"
        ),
    ]

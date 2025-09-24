from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE INDEX idx_user_role ON iltizam_users(role);",
            reverse_sql="DROP INDEX idx_user_role ON iltizam_users;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_user_active_role ON iltizam_users(is_active, role);",
            reverse_sql="DROP INDEX idx_user_active_role ON iltizam_users;"
        ),
    ]

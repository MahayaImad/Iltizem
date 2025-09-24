from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE INDEX idx_user_role ON iltizem_users(role);",
            reverse_sql="DROP INDEX idx_user_role ON iltizem_users;"
        ),
        migrations.RunSQL(
            "CREATE INDEX idx_user_active_role ON iltizem_users(is_active, role);",
            reverse_sql="DROP INDEX idx_user_active_role ON iltizem_users;"
        ),
    ]

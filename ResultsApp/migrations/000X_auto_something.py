from django.db import migrations

def set_defaults(apps, schema_editor):
    Result = apps.get_model('ResultsApp', 'Result')
    for idx, r in enumerate(Result.objects.all(), start=1):
        # Assign a test_type in a round-robin way
        if idx % 3 == 1:
            r.test_type = 'TEST1'
        elif idx % 3 == 2:
            r.test_type = 'TEST2'
        else:
            r.test_type = 'END_OF_TERM'

        # Assign a term (adjust as needed)
        r.term = 'TERM1'
        # Assign a year (adjust as needed)
        r.year = 2026
        r.save()

class Migration(migrations.Migration):

    dependencies = [
        ('ResultsApp', '0012_result_term_result_test_type_result_year_and_more'),  # adjust if needed
    ]

    operations = [
        migrations.RunPython(set_defaults),
    ]

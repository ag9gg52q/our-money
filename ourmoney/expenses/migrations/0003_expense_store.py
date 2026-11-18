from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('expenses', '0002_alter_expense_category_alter_expense_subcategory'),
    ]

    operations = [
        # Cheltuielile existente primesc un magazin gol; formularul îl cere la următoarea editare.
        migrations.AddField(
            model_name='expense',
            name='store',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]

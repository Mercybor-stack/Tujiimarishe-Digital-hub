# Fix Database Lock Issue - Instructions

## Quick Fix Steps:

### Step 1: Stop the Django Server
If your Django development server is running, stop it:
- Press `Ctrl+C` in the terminal where the server is running
- Or close the terminal window

### Step 2: Close Any Database Tools
- Close any SQLite browser tools (DB Browser, SQLiteStudio, etc.)
- Close any other applications that might be accessing the database

### Step 3: Try Again
- Restart your Django server: `python manage.py runserver`
- Try adding categories in the admin panel again

### Step 4: If Still Locked
If the issue persists, try these commands:

```bash
# Close all Python processes
taskkill /F /IM python.exe

# Wait a few seconds, then restart server
python manage.py runserver
```

## Alternative: Use Django Shell
If admin panel still has issues, add categories via Django shell:

```bash
python manage.py shell
```

Then run:
```python
from materials.models import SkillCategory

# Add Computer Literacy
cat1 = SkillCategory.objects.create(
    name="Computer Literacy",
    slug="computer-literacy",
    icon="fa-laptop",
    description="Learn basic computer skills, Microsoft Office, internet usage, and digital communication."
)

# Add Data Entry
cat2 = SkillCategory.objects.create(
    name="Data Entry",
    slug="data-entry",
    icon="fa-keyboard",
    description="Master data entry techniques, typing speed, accuracy, and data management skills."
)

print("Categories created successfully!")
```



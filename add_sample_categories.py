"""
Script to add sample skill categories to the database.
Run this with: python manage.py shell < add_sample_categories.py
Or run: python manage.py shell, then copy-paste the code below.
"""

from materials.models import SkillCategory

# Sample categories to add
categories_data = [
    {
        'name': 'Digital Marketing',
        'icon': 'fa-chart-line',
        'description': 'Learn digital marketing strategies, SEO, social media marketing, and online advertising to grow your business.',
        'slug': 'digital-marketing'
    },
    {
        'name': 'Graphic Design',
        'icon': 'fa-paint-brush',
        'description': 'Master graphic design tools like Photoshop, Illustrator, and Canva. Create stunning visuals for print and digital media.',
        'slug': 'graphic-design'
    },
    {
        'name': 'Web Development',
        'icon': 'fa-code',
        'description': 'Learn HTML, CSS, JavaScript, and modern web development frameworks to build professional websites.',
        'slug': 'web-development'
    },
    {
        'name': 'Data Analysis',
        'icon': 'fa-chart-bar',
        'description': 'Learn Excel, Python, and data visualization tools to analyze data and make data-driven decisions.',
        'slug': 'data-analysis'
    },
    {
        'name': 'Content Writing',
        'icon': 'fa-pen',
        'description': 'Develop your writing skills for blogs, social media, and marketing content. Learn SEO writing and copywriting.',
        'slug': 'content-writing'
    },
]

# Add categories
for cat_data in categories_data:
    category, created = SkillCategory.objects.get_or_create(
        slug=cat_data['slug'],
        defaults={
            'name': cat_data['name'],
            'icon': cat_data['icon'],
            'description': cat_data['description']
        }
    )
    if created:
        print(f"✓ Created: {category.name}")
    else:
        print(f"⚠ Already exists: {category.name}")

print(f"\nTotal categories: {SkillCategory.objects.count()}")



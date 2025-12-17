import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tujiimarishe.settings')
django.setup()

from materials.models import SkillCategory

print("=" * 50)
print("ALL CATEGORIES IN DATABASE:")
print("=" * 50)
all_cats = SkillCategory.objects.all().order_by('id')
for cat in all_cats:
    print(f"ID: {cat.id} | Name: '{cat.name}' | Slug: '{cat.slug}'")

print("\n" + "=" * 50)
print("COMPUTER LITERACY CATEGORIES:")
print("=" * 50)
computer_cats = SkillCategory.objects.filter(name__icontains='computer')
for cat in computer_cats:
    print(f"ID: {cat.id} | Name: '{cat.name}' | Slug: '{cat.slug}'")

print(f"\nTotal Computer Literacy categories: {computer_cats.count()}")

# If there are duplicates, delete all except the first one
if computer_cats.count() > 1:
    print("\n" + "=" * 50)
    print("DUPLICATES FOUND! Deleting extras...")
    print("=" * 50)
    # Keep the first one (lowest ID), delete the rest
    keep = computer_cats.order_by('id').first()
    duplicates = computer_cats.exclude(id=keep.id)
    
    for dup in duplicates:
        print(f"Deleting: ID {dup.id} - '{dup.name}' (Slug: '{dup.slug}')")
        dup.delete()
    
    print(f"\nKept: ID {keep.id} - '{keep.name}' (Slug: '{keep.slug}')")
    print("Duplicates deleted!")
else:
    print("\nNo duplicates found. Only one Computer Literacy category exists.")

print("\n" + "=" * 50)
print("FINAL RESULT:")
print("=" * 50)
final = SkillCategory.objects.filter(name__icontains='computer')
for cat in final:
    print(f"ID: {cat.id} | Name: '{cat.name}' | Slug: '{cat.slug}'")



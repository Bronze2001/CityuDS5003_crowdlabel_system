"""
Test data generator
Creates demo users, dog images, and annotations
"""
import os
import sys
import django
import random
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crowdlabel_backend.settings')
django.setup()

from api.models import User, Image, Annotation, Payment
from django.db import transaction

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

DOG_URL_TEMPLATE = "https://placedog.net/640/480?random={}"
TOTAL_IMAGES = 1000
ANNOTATOR_COUNT = 10
ANNOTATED_COUNT = 500
DISPUTE_COUNT = 100
RESOLVED_DISPUTE_COUNT = 80


def clear_existing_data():
    """Remove old demo data (keep admin)"""
    print("Cleaning existing data...")
    Annotation.objects.all().delete()
    Payment.objects.all().delete()
    Image.objects.all().delete()
    User.objects.filter(role='annotator').delete()
    print("  OK Cleared annotations, payments, images, and annotators")


def create_test_users():
    """Create admin and 10 annotators"""
    print("Creating test users...")

    admin, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin.set_password('admin123')
        admin.save()
        print("  OK Created admin user: admin/admin123")
    else:
        print("  - Admin user already exists (password unchanged)")

    annotators = []
    for i in range(1, ANNOTATOR_COUNT + 1):
        username = f'annotator{i}'
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'role': 'annotator'}
        )
        if created:
            user.set_password('123')
            user.save()
            print(f"  OK Created annotator: {username}/123")
        else:
            print(f"  - Annotator {username} already exists (password unchanged)")
        annotators.append(user)

    return admin, annotators


def generate_dog_image_urls(count: int):
    """Build unique dog image URLs"""
    return [DOG_URL_TEMPLATE.format(i) for i in range(1, count + 1)]


def create_test_images():
    """Create 1000 dog image tasks"""
    print("\nCreating 1000 dog images...")
    image_urls = generate_dog_image_urls(TOTAL_IMAGES)
    images = []
    for url in image_urls:
        image = Image.objects.create(
            image_url=url,
            category_options="Cat, Dog",
            bounty=Decimal("0.50"),
            status='active',
            review_status='none'
        )
        images.append(image)
    print(f"  OK Created {len(images)} image tasks")
    return images


def _pick_annotation_count():
    """Return uneven annotation count, prefer 5-8 to meet completion rule"""
    return random.choice([5, 5, 5, 6, 6, 7, 7, 8])


def _make_labels_for_dispute(count, pending):
    """Make labels with some Cat votes"""
    if count < 2:
        count = 2  # need at least 2 to have conflict
    num_cat = random.randint(1, max(1, min(2, count - 1)))
    labels = ['Cat'] * num_cat + ['Dog'] * (count - num_cat)
    random.shuffle(labels)
    if pending:
        correctness = [None] * count
    else:
        correctness = [label == 'Dog' for label in labels]
    return labels, correctness


def create_test_annotations(images, annotators):
    """Create annotations with disputes"""
    print("\nCreating annotations with disputes...")

    annotated_images = random.sample(images, ANNOTATED_COUNT)
    dispute_images = set(random.sample(annotated_images, DISPUTE_COUNT))
    resolved_disputes = set(random.sample(list(dispute_images), RESOLVED_DISPUTE_COUNT))
    total_annotations = 0
    for image in images:
        if image not in annotated_images:
            image.status = 'active'
            image.review_status = 'none'
            image.final_label = None
            image.assigned_count = 0
            image.save()
            continue

        is_dispute = image in dispute_images
        is_resolved = image in resolved_disputes

        ann_count = _pick_annotation_count()
        if is_dispute and ann_count < 2:
            ann_count = 2  # need conflict
        ann_count = min(ann_count, len(annotators))
        chosen_annotators = random.sample(annotators, ann_count)

        if not is_dispute:
            # No dispute: all Dog, auto approve
            labels = ['Dog'] * len(chosen_annotators)
            correctness = [True] * len(chosen_annotators)
            image.review_status = 'reviewed'
            image.final_label = 'Dog'
        elif is_resolved:
            labels, correctness = _make_labels_for_dispute(len(chosen_annotators), pending=False)
            image.review_status = 'reviewed'
            image.final_label = 'Dog'
        else:  # pending dispute
            labels, correctness = _make_labels_for_dispute(len(chosen_annotators), pending=True)
            image.review_status = 'pending'
            image.final_label = None

        for user, label, correct in zip(chosen_annotators, labels, correctness):
            Annotation.objects.create(
                user=user,
                image=image,
                submitted_label=label,
                is_correct=correct
            )
            total_annotations += 1

        image.assigned_count = len(chosen_annotators)

        # Align with app: completed only when assigned_count >= 5
        if image.assigned_count >= 5:
            image.status = 'completed'
        else:
            image.status = 'active'

        image.save()

    print(f"  OK Created annotations for {ANNOTATED_COUNT} images")
    print(f"  OK Total annotation records: {total_annotations}")
    print(f"  OK Disputes: {DISPUTE_COUNT} (resolved {RESOLVED_DISPUTE_COUNT}, pending {DISPUTE_COUNT - RESOLVED_DISPUTE_COUNT})")

def main():
    """Main function"""
    print("=" * 60)
    print("CrowdLabel System - Test Data Generator")
    print("=" * 60)
    
    try:
        clear_existing_data()
        with transaction.atomic():
            admin, annotators = create_test_users()
            images = create_test_images()
            create_test_annotations(images, annotators)
        
        print("\n" + "=" * 60)
        print("OK Test data generation completed successfully!")
        print("=" * 60)
        print("\nYou can now login with:")
        print("  Admin: admin / admin123")
        print("  Annotators: annotator1-10 / 123")
        print("\n")
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()


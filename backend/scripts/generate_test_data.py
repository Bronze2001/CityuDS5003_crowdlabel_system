"""
Test data generator script
Creates test users, images and annotations for demo
"""
import os
import sys
import django
from decimal import Decimal

# setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crowdlabel_backend.settings')
django.setup()

from api.models import User, Image, Annotation, Payment
from django.db import transaction

def create_test_users():
    """Create test users"""
    print("Creating test users...")
    
    # 创建管理员
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
        print(f"  ✓ Created admin user: admin/admin123")
    else:
        print(f"  - Admin user already exists")
    
    # 创建标注员
    annotators = []
    for i in range(1, 6):
        username = f'annotator{i}'
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'role': 'annotator'}
        )
        if created:
            user.set_password('123')
            user.save()
            annotators.append(user)
            print(f"  ✓ Created annotator: {username}/123")
        else:
            annotators.append(user)
            print(f"  - Annotator {username} already exists")
    
    return admin, annotators

def create_test_images():
    """Create test image tasks"""
    print("\nCreating test images...")
    
    # 示例图片 URL（Base64 或实际 URL）
    test_images = [
        {
            'url': 'https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=400',
            'categories': 'Cat, Dog, Bird',
            'bounty': Decimal('0.50')
        },
        {
            'url': 'https://images.unsplash.com/photo-1534361960057-19889db9621e?w=400',
            'categories': 'Cat, Dog, Bird',
            'bounty': Decimal('0.75')
        },
        {
            'url': 'https://images.unsplash.com/photo-1552053831-71594a27632d?w=400',
            'categories': 'Cat, Dog, Bird',
            'bounty': Decimal('1.00')
        },
        {
            'url': 'https://images.unsplash.com/photo-1517849845537-4d257902454a?w=400',
            'categories': 'Cat, Dog, Bird',
            'bounty': Decimal('0.50')
        },
        {
            'url': 'https://images.unsplash.com/photo-1517849845537-4d257902454a?w=400',
            'categories': 'Cat, Dog, Bird',
            'bounty': Decimal('0.60')
        },
    ]
    
    images = []
    for img_data in test_images:
        image, created = Image.objects.get_or_create(
            image_url=img_data['url'],
            defaults={
                'category_options': img_data['categories'],
                'bounty': img_data['bounty']
            }
        )
        if created:
            images.append(image)
            print(f"  ✓ Created image task #{image.id}: {img_data['categories']} (${img_data['bounty']})")
        else:
            images.append(image)
            print(f"  - Image task #{image.id} already exists")
    
    return images

def create_test_annotations(images, annotators):
    """Create test annotations"""
    print("\nCreating test annotations...")
    
    # 为每个图片创建一些标注
    labels_map = {
        0: 'Cat',    # 第一个标注员选 Cat
        1: 'Cat',    # 第二个标注员选 Cat
        2: 'Dog',    # 第三个标注员选 Dog（制造冲突）
        3: 'Cat',    # 第四个标注员选 Cat
        4: 'Cat',    # 第五个标注员选 Cat
    }
    
    annotation_count = 0
    for image in images:
        # 为前3个图片创建标注
        if image.id <= 3:
            for idx, annotator in enumerate(annotators[:5]):
                label = labels_map.get(idx, 'Cat')
                annotation, created = Annotation.objects.get_or_create(
                    user=annotator,
                    image=image,
                    defaults={'submitted_label': label}
                )
                if created:
                    annotation_count += 1
                    image.assigned_count += 1
                    image.save()
                    print(f"  ✓ User {annotator.username} annotated image #{image.id} as '{label}'")
    
    print(f"\n  Total annotations created: {annotation_count}")
    
    # 更新图片状态（如果达到5个标注）
    for image in images:
        if image.assigned_count >= 5:
            image.status = 'completed'
            anns = Annotation.objects.filter(image=image)
            labels = [a.submitted_label for a in anns]
            
            if len(set(labels)) == 1:
                image.review_status = 'reviewed'
                image.final_label = labels[0]
                anns.update(is_correct=True)
                print(f"  ✓ Image #{image.id} auto-approved: {labels[0]}")
            else:
                image.review_status = 'pending'
                print(f"  ⚠ Image #{image.id} requires review (conflict detected)")
            
            image.save()

def main():
    """Main function"""
    print("=" * 60)
    print("CrowdLabel System - Test Data Generator")
    print("=" * 60)
    
    try:
        with transaction.atomic():
            admin, annotators = create_test_users()
            images = create_test_images()
            create_test_annotations(images, annotators)
        
        print("\n" + "=" * 60)
        print("✓ Test data generation completed successfully!")
        print("=" * 60)
        print("\nYou can now login with:")
        print("  Admin: admin / admin123")
        print("  Annotators: annotator1-5 / 123")
        print("\n")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()


"""
Sample queries for demonstration
Run this script to test query performance
"""
import os
import sys
import time
import django

# setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crowdlabel_backend.settings')
django.setup()

from django.db import connection
from django.db.models import Sum, Count
from api.models import User, Image, Annotation, Payment

def print_separator():
    print("=" * 60)

def query_1_available_task(user_id=2):
    """Query 1: Get available task for annotator"""
    print("\n[Query 1] Get Available Task for Annotator")
    print_separator()
    
    start = time.time()
    
    done_ids = Annotation.objects.filter(user_id=user_id).values_list('image_id', flat=True)
    task = Image.objects.filter(
        status='active', 
        assigned_count__lt=5
    ).exclude(id__in=done_ids).order_by('-assigned_count').first()
    
    elapsed = (time.time() - start) * 1000
    
    print(f"User ID: {user_id}")
    print(f"Result: {task.id if task else 'No task available'}")
    print(f"Time: {elapsed:.2f}ms")
    
    # Show SQL
    print(f"\nSQL executed:")
    for query in connection.queries[-2:]:
        print(f"  {query['sql'][:100]}...")

def query_2_pending_balance(user_id=2):
    """Query 2: Calculate user's pending balance"""
    print("\n[Query 2] Calculate Pending Balance")
    print_separator()
    
    start = time.time()
    
    pending = Annotation.objects.filter(
        user_id=user_id, 
        is_correct=True, 
        payment__isnull=True
    ).aggregate(total=Sum('image__bounty'))['total'] or 0
    
    elapsed = (time.time() - start) * 1000
    
    print(f"User ID: {user_id}")
    print(f"Pending Balance: ${pending}")
    print(f"Time: {elapsed:.2f}ms")

def query_3_unpaid_users():
    """Query 3: Get users with unpaid balance"""
    print("\n[Query 3] Get Unpaid Users")
    print_separator()
    
    start = time.time()
    
    unpaid_data = Annotation.objects.filter(
        is_correct=True, 
        payment__isnull=True
    ).values('user__id', 'user__username').annotate(
        total_amount=Sum('image__bounty')
    ).filter(total_amount__gt=0)
    
    results = list(unpaid_data)
    elapsed = (time.time() - start) * 1000
    
    print(f"Found {len(results)} users with unpaid balance:")
    for item in results:
        print(f"  - {item['user__username']}: ${item['total_amount']}")
    print(f"Time: {elapsed:.2f}ms")

def query_4_user_accuracy(user_id=2):
    """Query 4: User accuracy rate"""
    print("\n[Query 4] User Accuracy Rate")
    print_separator()
    
    start = time.time()
    
    judged = Annotation.objects.filter(user_id=user_id, is_correct__isnull=False)
    total = judged.count()
    correct = judged.filter(is_correct=True).count()
    accuracy = (correct / total * 100) if total > 0 else 100.0
    
    elapsed = (time.time() - start) * 1000
    
    print(f"User ID: {user_id}")
    print(f"Total Judged: {total}")
    print(f"Correct: {correct}")
    print(f"Accuracy: {accuracy:.1f}%")
    print(f"Time: {elapsed:.2f}ms")

def query_5_review_queue():
    """Query 5: Get review queue for admin"""
    print("\n[Query 5] Admin Review Queue")
    print_separator()
    
    start = time.time()
    
    tasks = Image.objects.filter(review_status='pending')
    results = list(tasks.values('id', 'category_options', 'assigned_count'))
    
    elapsed = (time.time() - start) * 1000
    
    print(f"Found {len(results)} tasks pending review:")
    for task in results:
        print(f"  - Image #{task['id']}: {task['category_options']} ({task['assigned_count']} annotations)")
    print(f"Time: {elapsed:.2f}ms")

def show_statistics():
    """Show database statistics"""
    print("\n[Database Statistics]")
    print_separator()
    
    print(f"Users: {User.objects.count()}")
    print(f"Images: {Image.objects.count()}")
    print(f"Annotations: {Annotation.objects.count()}")
    print(f"Payments: {Payment.objects.count()}")
    print(f"Active Images: {Image.objects.filter(status='active').count()}")
    print(f"Pending Review: {Image.objects.filter(review_status='pending').count()}")

def main():
    print("=" * 60)
    print("CrowdLabel System - Query Performance Test")
    print("=" * 60)
    
    # Reset query log
    from django.db import reset_queries
    reset_queries()
    
    show_statistics()
    query_1_available_task()
    query_2_pending_balance()
    query_3_unpaid_users()
    query_4_user_accuracy()
    query_5_review_queue()
    
    print("\n" + "=" * 60)
    print("Query test completed!")
    print("=" * 60)

if __name__ == '__main__':
    main()


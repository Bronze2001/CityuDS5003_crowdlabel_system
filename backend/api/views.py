from django.db import transaction, models
from django.db.models import Sum, Q
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework.authentication import SessionAuthentication
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import logging
from .models import User, Image, Annotation, Payment
from .serializers import UserSerializer, ImageSerializer, AnnotationSerializer
from decimal import Decimal, InvalidOperation

logger = logging.getLogger(__name__)

# Skip CSRF check for API
class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return None

# Check if user is admin
class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

# ===== Auth APIs =====

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def login_view(request):
    """User login"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({'error': 'Username and password are required'}, status=400)
    
    user = authenticate(username=username, password=password)
    if user:
        login(request, user)
        logger.info(f'User {username} logged in')
        return Response(UserSerializer(user).data)
    logger.warning(f'Failed login attempt for username: {username}')
    return Response({'error': 'Invalid Credentials'}, status=400)

@api_view(['POST'])
@csrf_exempt
@authentication_classes([CsrfExemptSessionAuthentication])
def logout_view(request):
    """User logout"""
    if request.user.is_authenticated:
        logger.info(f'User {request.user.username} logged out')
    logout(request)
    return Response({'status': 'logged out'})

@api_view(['GET'])
def check_auth(request):
    """Check if user is logged in"""
    if request.user.is_authenticated:
        return Response(UserSerializer(request.user).data)
    return Response({'error': 'Not authenticated'}, status=401)

# ===== Annotator APIs =====

@api_view(['GET'])
def get_available_task(request):
    """Get next available task for annotator"""
    user = request.user
    done_ids = Annotation.objects.filter(user=user).values_list('image_id', flat=True)
    # find tasks not done by this user, prefer tasks close to completion
    task = Image.objects.filter(status='active', assigned_count__lt=5)\
        .exclude(id__in=done_ids)\
        .order_by('assigned_count').last()
    return Response(ImageSerializer(task).data if task else None)

@api_view(['POST'])
@csrf_exempt
@authentication_classes([CsrfExemptSessionAuthentication])
def submit_annotation(request):
    """Submit annotation for an image"""
    user = request.user
    image_id = request.data.get('image_id')
    label = request.data.get('label')

    if not image_id or not label:
        return Response({'error': 'image_id and label are required'}, status=400)
    
    if not isinstance(image_id, int):
        try:
            image_id = int(image_id)
        except (ValueError, TypeError):
            return Response({'error': 'Invalid image_id'}, status=400)

    try:
        with transaction.atomic():
            # lock the row to prevent race condition
            image = Image.objects.select_for_update().get(id=image_id)
            
            if image.status == 'completed':
                return Response({'error': 'Task completed'}, status=400)
            
            if Annotation.objects.filter(user=user, image=image).exists():
                return Response({'error': 'Already annotated'}, status=400)

            # check if label is valid
            valid_labels = [opt.strip() for opt in image.category_options.split(',')]
            if label not in valid_labels:
                return Response({'error': f'Invalid label. Must be one of: {", ".join(valid_labels)}'}, status=400)

            # save annotation
            Annotation.objects.create(user=user, image=image, submitted_label=label)
            image.assigned_count += 1
            
            # check consensus when 5 annotations collected
            if image.assigned_count >= 5:
                image.status = 'completed'
                anns = Annotation.objects.filter(image=image)
                labels = [a.submitted_label for a in anns]
                
                # if all 5 labels are the same, auto approve
                if len(set(labels)) == 1:
                    image.review_status = 'reviewed'
                    image.final_label = labels[0]
                    anns.update(is_correct=True)
                    logger.info(f'Image {image_id} auto-approved with label: {labels[0]}')
                else:
                    # conflict detected, need manual review
                    image.review_status = 'pending'
                    logger.info(f'Image {image_id} requires manual review (conflict detected)')
            
            image.save()
        logger.info(f'User {user.username} submitted annotation for image {image_id}')
        return Response({'status': 'success'})
    except Image.DoesNotExist:
        return Response({'error': 'Image not found'}, status=404)
    except IntegrityError as e:
        logger.error(f'Integrity error in submit_annotation: {str(e)}')
        return Response({'error': 'Database integrity error'}, status=400)
    except Exception as e:
        logger.error(f'Error in submit_annotation: {str(e)}', exc_info=True)
        return Response({'error': 'Internal server error'}, status=500)

@api_view(['GET'])
def get_user_stats(request):
    """Get user statistics"""
    user = request.user
    # pending balance: correct but not paid yet
    pending = Annotation.objects.filter(user=user, is_correct=True, payment__isnull=True)\
        .aggregate(total=Sum('image__bounty'))['total'] or 0
    
    # accuracy: only count judged annotations
    judged = Annotation.objects.filter(user=user, is_correct__isnull=False)
    total = judged.count()
    correct = judged.filter(is_correct=True).count()
    acc = (correct / total) if total > 0 else 1.0

    return Response({
        'pendingBalance': pending,
        'accuracy': acc,
        'totalAnnotated': Annotation.objects.filter(user=user).count(),
        'correctCount': correct
    })

@api_view(['GET'])
def get_user_history(request):
    """Get user annotation history"""
    anns = Annotation.objects.filter(user=request.user).order_by('-created_at')
    return Response(AnnotationSerializer(anns, many=True).data)

# ===== Admin APIs =====

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_review_queue(request):
    """Get tasks that need manual review"""
    tasks = Image.objects.filter(review_status='pending')
    return Response(ImageSerializer(tasks, many=True).data)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_all_active_tasks(request):
    """Get all active tasks"""
    tasks = Image.objects.filter(status='active')
    return Response(ImageSerializer(tasks, many=True).data)

@api_view(['POST'])
@permission_classes([IsAdminUser])
@csrf_exempt
@authentication_classes([CsrfExemptSessionAuthentication])
def add_task(request):
    """Add a new task"""
    url = request.data.get('url')
    categories = request.data.get('categories')
    bounty = request.data.get('bounty')
    
    # validate input
    if not url or not categories:
        return Response({'error': 'url and categories are required'}, status=400)
    
    if not isinstance(url, str) or len(url.strip()) == 0:
        return Response({'error': 'Invalid url'}, status=400)
    
    if not isinstance(categories, str) or len(categories.strip()) == 0:
        return Response({'error': 'Invalid categories'}, status=400)
    
    # validate bounty
    try:
        bounty = Decimal(str(bounty)) if bounty is not None else Decimal('0.50')
        if bounty < 0:
            return Response({'error': 'Bounty must be non-negative'}, status=400)
        if bounty > 1000:
            return Response({'error': 'Bounty too large (max 1000)'}, status=400)
    except (ValueError, InvalidOperation, TypeError):
        return Response({'error': 'Invalid bounty value'}, status=400)
    
    try:
        Image.objects.create(
            image_url=url.strip(),
            category_options=categories.strip(),
            bounty=bounty
        )
        logger.info(f'Admin {request.user.username} created new task with bounty {bounty}')
        return Response({'status': 'created'})
    except Exception as e:
        logger.error(f'Error in add_task: {str(e)}', exc_info=True)
        return Response({'error': 'Failed to create task'}, status=500)

@api_view(['POST'])
@permission_classes([IsAdminUser])
@csrf_exempt
@authentication_classes([CsrfExemptSessionAuthentication])
def resolve_conflict(request):
    """Resolve conflict by setting the correct label"""
    img_id = request.data.get('image_id')
    true_label = request.data.get('true_label')
    
    if not img_id or not true_label:
        return Response({'error': 'image_id and true_label are required'}, status=400)
    
    if not isinstance(img_id, int):
        try:
            img_id = int(img_id)
        except (ValueError, TypeError):
            return Response({'error': 'Invalid image_id'}, status=400)
    
    try:
        with transaction.atomic():
            img = Image.objects.get(id=img_id)
            
            # check if label is valid
            valid_labels = [opt.strip() for opt in img.category_options.split(',')]
            if true_label not in valid_labels:
                return Response({'error': f'Invalid label. Must be one of: {", ".join(valid_labels)}'}, status=400)
            
            img.final_label = true_label
            img.review_status = 'reviewed'
            img.save()
            
            # mark annotations as correct or wrong
            Annotation.objects.filter(image=img, submitted_label=true_label).update(is_correct=True)
            Annotation.objects.filter(image=img).exclude(submitted_label=true_label).update(is_correct=False)
        
        logger.info(f'Admin {request.user.username} resolved conflict for image {img_id} with label: {true_label}')
        return Response({'status': 'resolved'})
    except Image.DoesNotExist:
        return Response({'error': 'Image not found'}, status=404)
    except Exception as e:
        logger.error(f'Error in resolve_conflict: {str(e)}', exc_info=True)
        return Response({'error': 'Failed to resolve conflict'}, status=500)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_unpaid_users(request):
    """Get list of users with unpaid balance"""
    unpaid_data = Annotation.objects.filter(
        is_correct=True, 
        payment__isnull=True
    ).values('user__id', 'user__username').annotate(
        total_amount=Sum('image__bounty')
    ).filter(total_amount__gt=0)
    
    data = [
        {
            'userId': item['user__id'],
            'username': item['user__username'],
            'amount': item['total_amount']
        }
        for item in unpaid_data
    ]
    
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAdminUser])
@csrf_exempt
@authentication_classes([CsrfExemptSessionAuthentication])
def run_payroll(request):
    """Process payments for all unpaid annotations"""
    try:
        with transaction.atomic():
            payable = Annotation.objects.filter(is_correct=True, payment__isnull=True).select_related('image', 'user')
            if not payable.exists():
                return Response({'total': 0})
            
            # calculate amount for each user
            payouts = {}
            for a in payable:
                payouts[a.user.id] = payouts.get(a.user.id, Decimal(0)) + a.image.bounty
                
            total = Decimal(0)
            for uid, amt in payouts.items():
                pmt = Payment.objects.create(annotator_id=uid, amount=amt)
                # mark as paid
                Annotation.objects.filter(user_id=uid, is_correct=True, payment__isnull=True).update(payment=pmt)
                # update wallet balance
                User.objects.filter(id=uid).update(balance_wallet=models.F('balance_wallet') + amt)
                total += amt
                logger.info(f'Payment processed for user {uid}: ${amt}')
            
        logger.info(f'Admin {request.user.username} ran payroll: total ${total}')
        return Response({'total': float(total)})
    except Exception as e:
        logger.error(f'Error in run_payroll: {str(e)}', exc_info=True)
        return Response({'error': 'Failed to process payroll'}, status=500)

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db import IntegrityError
from .models import User, Disability, Food_type, Business, Business_review, Business_facility ,User_Business_visits, Image
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
import logging
import base64
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import ImageSerializer
from django.contrib.sessions.middleware import SessionMiddleware


logger = logging.getLogger(__name__)

@csrf_exempt
def register(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        confirmation = data.get("confirmation")
        
        if password != confirmation:
            return JsonResponse({"message": "Passwords don't match", "status":"failed"}, status=403)
        
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except:
            return JsonResponse({"message": "Username aleady taken", "status":"failed"}, status=403)
        try:
            login(request, user)
            return JsonResponse({"message": "Username logged in", "status":"success"}, status=200)
        except:
            return JsonResponse({"message": "Couldn't log in", "status":"failed"}, status=403)
    else:
        return JsonResponse({"message": "Invalid method", "status":"failed"}, status=403)

@csrf_exempt
def login_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        logging.warning("incerc sa autentific " + username + password )
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            logging.warning(request.user)
            session_key = request.session.session_key
            logger.warning(f'Session key after login: {session_key}')
            return JsonResponse({"message": "Username logged in", "status":"success"}, status=200)
        else:
            return JsonResponse({"message": "Username or password incorrect", "status":"failed"}, status=403)
    return JsonResponse({"message": "POST request needed", "status":"failed"}, status=400)

@csrf_exempt
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return JsonResponse({"message": "Username logged out", "status":"success"}, status=200)

@login_required
@csrf_exempt
def user_view(request):
    if request.method == "GET":
        if not request.user:
             return JsonResponse({"message": "Username not logged in", "status":"failed"}, status=403)
        user = request.user
        
        return JsonResponse(user.serializer())
    
    elif request.method == "PUT":
        data = json.loads(request.body)
        user = request.user
        
        if data.get("username"):
            user.username = data.get("username")
        
        if data.get("email"):
            user.email = data.get("email")
            
        if data.get("disabilities"):
            disabiliteis = data.get("disability")
            for disability_item in disabiliteis:

                if not user.diasabilities.filter(name=disability_item["name"]).exists():
                    disability = Disability.objects.filter(name=disability_item["name"], severity=disability_item["severity"])
                    user.disabilities.add(disability)
                    user.save()
                
        if data.get("foodPreferences"):
            preferences = data.get("foodPreferences")
            for preference in preferences:
                if not user.food_preferences.filter(name=preference["name"]).exists():
                    preference = Food_type.objects.filter(name=preference["name"])
                    user.food_preferences.add(preference)
                    user.save()
            
        return JsonResponse({"message": "Changes applied", "status":"success"}, status=200)
        

@csrf_exempt
def business_post_view(request):
    logging.warning('blabla')
    if request.method == "POST":
        logging.warning(request.user)
        try:
            # Get the data from the POST request
            name = request.POST.get("name")
            price_rating = request.POST.get("price_rating")
            business_type = request.POST.get("business_type")
            address = request.POST.get("address")
            website = request.POST.get("website")
            phone_number = request.POST.get("phone_number")
            rating = request.POST.get("rating")
            locomotor_rating = request.POST.get("locomotor_rating")
            visual_rating = request.POST.get("visual_rating")
            hearing_rating = request.POST.get("hearing_rating")

            # Ensure the user is authenticated
            owner = request.user
            if not owner.is_authenticated:
                return JsonResponse({"message": "User not authenticated"}, status=403)

            # Logging for debugging
            logger.info(f"Creating business: {name}, Owner: {owner.username}")

            # Check if a business with this name already exists
            if Business.objects.filter(name=name).exists():
                return JsonResponse({"message": "Business already exists"}, status=403)

            # Create the business
            business = Business.objects.create(
                name=name,
                owner=owner,
                price_rating=price_rating,
                business_type=business_type,
                address=address,
                website=website,
                phone_number=phone_number,
                rating=rating,
                locomotor_rating=locomotor_rating,
                visual_rating=visual_rating,
                hearing_rating=hearing_rating
            )

            # Save associated images (if any)
            for image in request.FILES.getlist('images'):
                Image.objects.create(business=business, name=image.name, image=image)

            # Return success response
            return JsonResponse({"message": "Business created"}, status=201)

        except Exception as e:
            logger.error(f"Error creating business: {str(e)}")
            return JsonResponse({"message": f"Error: {str(e)}"}, status=500)

@csrf_exempt
def business_reviews(request, id):
    if request.method == "GET":
        business = Business.objects.filter(pk=id)

        if business.exists():
            reviews = business.reviews

        return JsonResponse([review.serialize() for review in reviews], safe=False)
    else:
        #Get data
        data = json.loads(request.body)
        title = data.get("title")
        content = data.get("content")
        rating = data.get("rating")
        locomotor_rating = data.get("locomotor_rating")
        visual_rating = data.get("visual_rating")
        hearing_rating = data.get("hearing_rating")
        business_id = data.get("business_id")

        #Get the business the review is written for
        business = get_object_or_404(Business, pk=business_id)

        user = request.user

        try:
            review = Business_review.objects.create(creator=user, business=business, title=title, content=content, rating=rating, locomotor_rating=locomotor_rating, visual_rating=visual_rating ,hearing_rating=hearing_rating)
            review.save()
            return JsonResponse({"message": "Review created"}, status=200)
        except:
            return JsonResponse({"message": "Review creation faile"}, status=403)

@csrf_exempt
def businesses_view(request):
    if request.method == "GET":
        logger.warning("Entering businesses_view")
        logger.warning(request.user)

        # Get all businesses
        businesses = Business.objects.all()

        # Serialize all businesses including images and reviews
        serialized_businesses = [business.serializer() for business in businesses]

        # Return the serialized list as a JSON response
        return JsonResponse(serialized_businesses, safe=False)

    else:  # Handle POST requests for filtering businesses
        data = json.loads(request.body)
        location = data.get("location")
        business_types = data.get("type", [])
        selection_criteria = data.get("dissabilities", [])  # List of criteria, e.g., ['locomotor', 'visual']
        
        # Filter by location and business types
        businesses_list = Business.objects.filter(
            address__icontains=location, 
            business_type__in=business_types
        )
        
        ordering_criteria = []
        
        if "locomotor" in selection_criteria:
            ordering_criteria.append("-locomotor_rating")
        if "visual" in selection_criteria:
            ordering_criteria.append("-visual_rating")
        if "hearing" in selection_criteria:
            ordering_criteria.append("-hearing_rating")
        
        ordering_criteria.append('-rating')
        
        businesses_list = businesses_list.order_by(*ordering_criteria)
        
        # Serialize the filtered businesses including images and reviews
        serialized_businesses = [business.serializer() for business in businesses_list]
        
        return JsonResponse(serialized_businesses, safe=False, status=200)


@csrf_exempt
def user_disabilities(request):
    if request.method == "GET":
        if request.user == None:
            return JsonResponse({"disabilities": []}, safe=False)
        
        disabilities_list = request.user.get_disabilities()
        
        return JsonResponse({"disabilities": disabilities_list}, safe=False)
    
def visit(request):
    if request.method == "GET":
        user = request.user
        
        businesses = User_Business_visits.objects.filter(user=user)
        
        serialized_businesses = [business.serialize() for business in businesses]
        return JsonResponse(serialized_businesses, safe=False, status=200)
    else:
        data = json.loads(request.body)
        try:
            user = request.user
        except:
            return
        business_id = data.get("business_id")
        
        sel_business = get_object_or_404(Business, pk=business_id)
        
        #create relationship
        visit = User_Business_visits.objects.create(user=user, business=sel_business)
        visit.save()
        
        return JsonResponse(status=403)
    
    
def user_reviews(request):
    if request.method == "GET":
        reviews = request.user.reviews
        reviews_list = []
        for review in reviews:
            review_content = {"title": review.title, "content": review.content, "rating": review.rating, "date_time_posted": review.date_time_posted}
            reviews_list.append(review_content)
        return JsonResponse({"reviews": reviews_list})
    else:
        return JsonResponse(status=403)

@csrf_exempt
def user_favorites(request):
    if request.method == "GET":
        favorite_businesses = request.user.favorites.all()
        serialized_businesses = []
        
        for business in favorite_businesses:
            serialized_businesses.append(business.serializer())
            
        return JsonResponse({"favorites": serialized_businesses}, status=200)
        
    elif request.method == "POST":
        data = json.loads(request.body)
        business_id = data.get("business_id")
        isFavorite = data.get("isFavorite")

        business = get_object_or_404(Business, pk=business_id)

        if isFavorite is True:
            # Add business to user's favorites
            request.user.favorites.add(business)
            message = "Business added to favorites"
        else:
            # Remove business from user's favorites
            request.user.favorites.remove(business)
            message = "Business removed from favorites"

        return JsonResponse({"message": message}, status=200)
        
# class ImageView(APIView):
#     parser_classes = (MultiPartParser, FormParser)
    
#     def post(self, request, *args, **kwargs):
#         image_file = request.FILES['image']
#         image_name = request.data['name']
            
#         # Read the binary data
#         image_data = image_file.read()
            
#         # Save the image
#         image_instance = Image.objects.create(name=image_name, image=image_data)
#         serializer = ImageSerializer(image_instance)
            
#         return Response(serializer.data)
        
#     def get(self, request, *args, **kwargs):
#         image_id = kwargs.get('id')
#         image_instance = Image.objects.get(id=image_id)
#         image_data = base64.b64encode(image_instance.image).decode('utf-8')
            
#         response_data = {
#             'id': image_instance.id,
#             'name': image_instance.name,
#             'image': image_data,
#         }
            
#         return Response(response_data)
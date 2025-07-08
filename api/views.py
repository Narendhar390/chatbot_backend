from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
# class RegisterView(APIView):
#     def post(self, request):
#         data = request.data
#         if User.objects.filter(username=data['email']).exists():
#             return Response({"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)

#         user = User.objects.create(
#             username=data['email'],
#             email=data['email'],
#             first_name=data.get('name', ''),
#             password=make_password(data['password']),
#         )

#         return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
# class ChatView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         message = request.data.get("message")
#         bot_reply = "Dummy reply: from views " + message
#         return Response({ "reply": bot_reply})
# Create your views here.
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterView(APIView):
    def post(self, request):
        data = request.data

        if User.objects.filter(username=data['email']).exists():
            return Response({"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=data['email'],
            email=data['email'],
            first_name=data.get('name', ''),
            password=data['password']
        )

        # 🔑 Generate tokens after registration
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        return Response({
            "message": "User registered successfully",
            "access": str(access),
            "refresh": str(refresh),
        }, status=status.HTTP_201_CREATED)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import openai
import os
import json
from api.nlp_chatbot import HealthcareChatbot

chatbot = HealthcareChatbot('api/health_qa.csv')
from dotenv import load_dotenv
load_dotenv()  # This loads variables from .env into environment

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")




def is_healthcare_related(message):
    keywords = [ # General
        "health", "medicine", "fitness", "doctor", "hospital", "treatment", "clinic",

        # Symptoms
        "symptom", "cough", "fever", "pain", "nausea", "vomiting", "dizziness", "rash", "itching",
        "sore throat", "headache", "fatigue", "swelling", "diarrhea", "constipation",

        # Conditions & Diseases
        "disease", "diabetes", "cancer", "covid", "fracture", "injury", "infection", "allergy", "asthma",
        "hypertension", "obesity", "anxiety", "depression", "stroke", "arthritis", "ulcer", "eczema",
        "hepatitis", "migraine", "anemia", "flu", "tuberculosis", "thyroid", "pneumonia", "jaundice", "malaria",

        # Diagnostics & Procedures
        "vaccine", "x-ray", "mri", "ct scan", "ultrasound", "endoscopy", "biopsy", "surgery", "checkup",
        "ecg", "blood test", "dialysis", "transplant", "chemotherapy", "radiation",

        # Metrics
        "blood pressure", "bp", "heart rate", "bmi", "cholesterol", "oxygen level", "pulse",

        # Specialists
        "cardiology", "neurology", "dermatology", "gynecology", "pediatrics", "psychiatry", "urology",
        "orthopedics", "radiology", "gastroenterology", "endocrinology", "nephrology", "pulmonology",

        # People & Services
        "surgeon", "nurse", "paramedic", "therapist", "specialist", "appointment", "consultation",
        "ambulance", "insurance", "pharmacy", "prescription",

        # Medications
        "antibiotic", "antiviral", "painkiller", "analgesic", "antidepressant", "vitamin", "supplement",
        "insulin", "ointment", "syrup", "capsule", "tablet",

        # Others
        "suffering", "cold", "cure", "therapy", "illness",'treat','nervous','feel']
    message = message.lower()
    return any(keyword in message for keyword in keywords)
def isGreeting(message):
    keywords=["hi","hello",]
    message = message.lower()
    return any(keyword in message for keyword in keywords)
@csrf_exempt
@require_http_methods(["POST"])
@permission_classes([IsAuthenticated])
def chat(request):
    try:
        body = json.loads(request.body)
        user_message = body.get("message", "")
        print(f"👤 User: {user_message}")

        if not is_healthcare_related(user_message):
            if isGreeting(user_message):
                return JsonResponse({
                    "reply":"Hi ,welcome to ai powed chatbot kindly ask only health related quries."
                })
            return JsonResponse({
                "reply": "I'm only allowed to answer questions related to healthcare. Please ask me something about health, symptoms, or medicine."
            })

        messages = [
            {"role": "system", "content": "You are a helpful healthcare assistant. Answer only health-related questions."},
            {"role": "user", "content": user_message}
        ]

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.6,
            max_tokens=300
        )
        reply = response.choices[0].message.content.strip()
        print(f"🤖 Bot: {reply}")
        return JsonResponse({"reply": reply})

    except Exception as e:
        print("❌ GPT API ERROR:", e)
        return JsonResponse({"reply": "Sorry, something went wrong."}, status=500)
@require_http_methods(["POST"])
# @permission_classes([IsAuthenticated])
@csrf_exempt
def chat_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "")
        bot_reply = chatbot.get_response(user_message)
        print("bot_reply")
        return JsonResponse({"reply": bot_reply})
    
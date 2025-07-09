from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken

import openai
import os
import json

from dotenv import load_dotenv
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


# ✅ Keyword checker for health topics
def is_healthcare_related(message):
    keywords = [
        "health", "medicine", "fitness", "doctor", "hospital", "treatment", "clinic",
        "symptom", "cough", "fever", "pain", "nausea", "vomiting", "dizziness", "rash",
        "sore throat", "headache", "fatigue", "swelling", "diarrhea", "constipation",
        "disease", "diabetes", "cancer", "covid", "fracture", "injury", "infection",
        "allergy", "asthma", "hypertension", "obesity", "anxiety", "depression", "stroke",
        "arthritis", "ulcer", "eczema", "hepatitis", "migraine", "anemia", "flu",
        "thyroid", "pneumonia", "jaundice", "malaria", "vaccine", "x-ray", "mri",
        "ct scan", "ultrasound", "endoscopy", "biopsy", "surgery", "checkup", "ecg",
        "blood test", "dialysis", "transplant", "chemotherapy", "radiation",
        "blood pressure", "bp", "heart rate", "bmi", "cholesterol", "oxygen level",
        "pulse", "cardiology", "neurology", "dermatology", "gynecology", "pediatrics",
        "psychiatry", "urology", "orthopedics", "radiology", "gastroenterology",
        "endocrinology", "nephrology", "pulmonology", "surgeon", "nurse", "paramedic",
        "therapist", "specialist", "appointment", "consultation", "ambulance", "insurance",
        "pharmacy", "prescription", "antibiotic", "antiviral", "painkiller", "analgesic",
        "antidepressant", "vitamin", "supplement", "insulin", "ointment", "syrup",
        "capsule", "tablet", "suffering", "cold", "cure", "therapy", "illness", "treat", "nervous", "feel"
    ]
    message = message.lower()
    return any(keyword in message for keyword in keywords)


# ✅ Greeting check
def isGreeting(message):
    keywords = ["hi", "hello", "hey", "good morning", "good evening"]
    message = message.lower()
    return any(keyword in message for keyword in keywords)


# ✅ User Registration API
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

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        return Response({
            "message": "User registered successfully",
            "access": str(access),
            "refresh": str(refresh),
        }, status=status.HTTP_201_CREATED)


# ✅ Chatbot API (JWT Protected)
class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_message = request.data.get("message", "").strip()
        print(f"👤 User: {user_message}")

        if not user_message:
            return Response({"reply": "Please send a message to continue."}, status=400)

        if not is_healthcare_related(user_message):
            if isGreeting(user_message):
                return Response({
                    "reply": "Hi, welcome to the AI-powered chatbot. Kindly ask only health-related queries."
                })
            return Response({
                "reply": "I'm only allowed to answer questions related to healthcare. Please ask me something about health, symptoms, or medicine."
            })

        messages = [
            {"role": "system", "content": "You are a helpful healthcare assistant. Answer only health-related questions."},
            {"role": "user", "content": user_message}
        ]

        try:
            response = openai.chat.completions.create(
                model="gpt-4o",  # Replace with your approved model
                messages=messages,
                temperature=0.6,
                max_tokens=300
            )
            reply = response.choices[0].message.content.strip()
            print(f"🤖 Bot: {reply}")
            return Response({"reply": reply})

        except Exception as e:
            print("❌ GPT API ERROR:", e)
            return Response({"reply": "Sorry, something went wrong."}, status=500)

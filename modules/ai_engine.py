# import time
# import json
# import os
# from google import genai
# from google.genai import types

# class QuizEngine:
#     def __init__(self, api_key):
#         """Initializes the Gemini Client."""
#         self.client = genai.Client(api_key=api_key)
        
#         # FIX: Remove the 'models/' prefix. 
#         # Also updated to the current stable 'gemini-1.5-flash' or 'gemini-2.0-flash'
#         self.model_id = "gemini-2.5-flash"

#     def generate_quiz(self, file_path, count, difficulty, lang, exam_type):
#         """Generates quiz with specific exam patterns and error handling."""
        
#         # # 1. UPLOAD
#         # uploaded_file = self.client.files.upload(file=file_path)
        
#         # # 2. POLLING
#         # while uploaded_file.state == "PROCESSING":
#         #     time.sleep(2)
#         #     uploaded_file = self.client.files.get(name=uploaded_file.name)

#         # prompt = f"""
#         # Role: Senior Question Setter for {exam_type} Bangladesh.
#         # Task: Create {count} MCQ questions in {lang} from the attached document.
#         # Requirements:
#         # - Output a JSON array ONLY.
#         # - Keys: 'q', 'options', 'correct_idx', 'explanation', 'ref'.
#         # """

#     # 1. UPLOAD (SDK handles PDF and Image automatically)
#         uploaded_file = self.client.files.upload(file=file_path)
        
#         # 2. POLLING
#         while uploaded_file.state == "PROCESSING":
#             time.sleep(2)
#             uploaded_file = self.client.files.get(name=uploaded_file.name)

#         # 3. PROMPT (Optimized for OCR/Images)
#         prompt = f"""
#         Role: Senior Exam Expert.
#         Task: Extract information from this {file_path.split('.')[-1]} and create {count} MCQ questions.
#         Language: {lang}. Exam: {exam_type}.
#         Note: If this is an image, perform high-accuracy OCR first. 
#         Output: JSON array with keys: 'q', 'options', 'correct_idx', 'explanation', 'ref'.
#         """

#         # 3. SMART RETRY LOGIC (Exponential Backoff)
#         max_retries = 3
#         for attempt in range(max_retries):
#             try:
#                 # The SDK handle the 'models/' pathing internally
#                 response = self.client.models.generate_content(
#                     model=self.model_id,
#                     contents=[uploaded_file, prompt],
#                     config=types.GenerateContentConfig(
#                         response_mime_type="application/json",
#                         temperature=0.7
#                     )
#                 )
#                 self.client.files.delete(name=uploaded_file.name)
#                 return json.loads(response.text)

#             except Exception as e:
#                 err_msg = str(e).lower()
                
#                 # Check for Rate Limit (429) - still keep this for the Free Tier
#                 if "429" in err_msg or "resource_exhausted" in err_msg:
#                     if attempt < max_retries - 1:
#                         time.sleep(32)
#                         continue
                
#                 try: self.client.files.delete(name=uploaded_file.name)
#                 except: pass
#                 raise Exception(f"AI Engine Error: {str(e)}")









# import time
# import json
# import os
# import random
# import logging
# from google import genai
# from google.genai import types

# # -----------------------------
# # Configure Logging
# # -----------------------------
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s | %(levelname)s | %(message)s"
# )

# class QuizEngine:
#     def __init__(self, api_key):
#         """Initializes the Gemini Client."""
#         self.client = genai.Client(api_key=api_key)
#         self.model_id = "gemini-2.5-flash"
#         logging.info("QuizEngine initialized with model: %s", self.model_id)

#     def generate_quiz(self, file_path, count, difficulty, lang, exam_type):
#         """Generates a quiz from PDF or image with retries, OCR auto-detection, and clean JSON."""
        
#         ext = file_path.split('.')[-1].lower()
#         is_image = ext in ["jpg", "jpeg", "png"]

#         logging.info("Generating quiz from file: %s | Type: %s | Questions: %d | Lang: %s | Exam: %s",
#                      file_path, "Image" if is_image else "PDF", count, lang, exam_type)

#         # -----------------------------
#         # Upload file to Gemini SDK
#         # -----------------------------
#         uploaded_file = self.client.files.upload(file=file_path)

#         # Poll until processing is done
#         while uploaded_file.state == "PROCESSING":
#             logging.info("File processing... waiting 2s")
#             time.sleep(2)
#             uploaded_file = self.client.files.get(name=uploaded_file.name)

#         # -----------------------------
#         # Build dynamic prompt
#         # -----------------------------
#         prompt = f"""
# Role: Senior Exam Expert.
# Task: Extract information from this {ext} and create {count} MCQ questions.
# Language: {lang}. Exam: {exam_type}.
# Difficulty: {difficulty}.
# {"Perform high-accuracy OCR since this is an image." if is_image else ""}
# Output: JSON array with keys: 'q', 'options', 'correct_idx', 'explanation', 'ref'.
# """

#         # -----------------------------
#         # Retry logic with exponential backoff + jitter
#         # -----------------------------
#         max_retries = 3
#         base_delay = 5  # seconds

#         for attempt in range(max_retries):
#             try:
#                 response = self.client.models.generate_content(
#                     model=self.model_id,
#                     contents=[uploaded_file, prompt],
#                     config=types.GenerateContentConfig(
#                         response_mime_type="application/json",
#                         temperature=0.7
#                     )
#                 )

#                 # Delete uploaded file to free storage
#                 try:
#                     self.client.files.delete(name=uploaded_file.name)
#                 except Exception:
#                     logging.warning("Could not delete uploaded file: %s", uploaded_file.name)

#                 # Parse JSON
#                 data = json.loads(response.text)
#                 if not isinstance(data, list):
#                     raise Exception("AI Engine did not return a JSON array")
#                 logging.info("Quiz generated successfully with %d questions", len(data))
#                 return data

#             except Exception as e:
#                 err_msg = str(e).lower()
#                 logging.error("Attempt %d failed: %s", attempt + 1, e)

#                 # Retry only for rate limits or transient errors
#                 if "429" in err_msg or "resource_exhausted" in err_msg:
#                     delay = base_delay * (2 ** attempt) + random.uniform(0, 3)
#                     logging.info("Rate limit hit. Retrying in %.1f seconds...", delay)
#                     time.sleep(delay)
#                     continue

#                 # If non-retryable error, raise
#                 try:
#                     self.client.files.delete(name=uploaded_file.name)
#                 except:
#                     pass
#                 raise Exception(f"AI Engine Error: {str(e)}")

#         # If retries exhausted
#         raise Exception("Failed to generate quiz after multiple retries.")

import time
import json
import random
import logging
from google import genai
from google.genai import types

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

class QuizEngine:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        # Primary and Backup models for 2026
        self.model_pool = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
        logging.info("QuizEngine initialized with Model Fallback Pool.")

    def generate_quiz(self, file_path, count, difficulty, lang, exam_type):
        ext = file_path.split('.')[-1].lower()
        
        # Category specific logic for the prompt
        category_guidelines = {
            "BCS": "Focus on high-level analytical ability and precise Civil Service standards.",
            "NTRCA": "Focus on pedagogical knowledge and subject-specific teaching concepts.",
            "Primary": "Focus on primary education recruitment standards and logic.",
            "Bank Job": "Emphasize mathematics, analytical puzzles, and financial trends.",
            "Admission": "Focus on academic deep-dives and rapid-fire university entrance style."
        }
        exam_rule = category_guidelines.get(exam_type, "Standard competitive exam assessment.")

        # Upload file
        uploaded_file = self.client.files.upload(file=file_path)
        while uploaded_file.state == "PROCESSING":
            time.sleep(2)
            uploaded_file = self.client.files.get(name=uploaded_file.name)

        prompt = f"""
        Role: Expert Question Setter for {exam_type}.
        Guidelines: {exam_rule}
        Task: Create {count} MCQ questions from this {ext}. Lang: {lang}. Difficulty: {difficulty}.
        Return ONLY a JSON array with: 'q', 'options', 'correct_idx', 'explanation'.
        """

        # Loop through models in the pool if one fails
        for model_id in self.model_pool:
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    logging.info(f"Attempting {model_id} (Try {attempt + 1})")
                    response = self.client.models.generate_content(
                        model=model_id,
                        contents=[uploaded_file, prompt],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            temperature=0.7
                        )
                    )
                    
                    # Cleanup and return
                    self.client.files.delete(name=uploaded_file.name)
                    return json.loads(response.text)

                except Exception as e:
                    err_msg = str(e).lower()
                    if "429" in err_msg or "resource_exhausted" in err_msg:
                        wait = 10 + random.uniform(0, 5)
                        logging.warning(f"Rate limit hit. Waiting {wait:.1f}s...")
                        time.sleep(wait)
                        continue
                    logging.error(f"Model {model_id} failed: {e}")
                    break # Try next model in pool

        # Final Cleanup if everything fails
        try: self.client.files.delete(name=uploaded_file.name)
        except: pass
        raise Exception("The AI is currently overwhelmed. Please wait 1 minute and try again.")
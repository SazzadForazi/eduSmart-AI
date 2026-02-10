

# import datetime
# import streamlit as st
# import os, tempfile, time, json
# from dotenv import load_dotenv
# from modules.ai_engine import QuizEngine

# # -----------------------------
# # 1. SETUP & ASSETS
# # -----------------------------
# load_dotenv()

# def load_assets():
#     st.markdown("""
#         <style>
#         .main { background-color: #0e1117; }
#         .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
#         [data-testid="stSidebar"] { background-color: #0d1117; }
#         .question-card {
#             background-color: #161b22;
#             padding: 20px;
#             border-radius: 10px;
#             border: 1px solid #30363d;
#             margin-bottom: 15px;
#             color: white;
#         }
#         </style>
#     """, unsafe_allow_html=True)
    
#     if os.path.exists("assets/style.css"):
#         with open("assets/style.css") as f:
#             st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# load_assets()

# # Initialize AI Engine
# engine = QuizEngine(os.getenv("GEMINI_API_KEY"))

# # -----------------------------
# # 2. SESSION STATE
# # -----------------------------
# if "step" not in st.session_state: st.session_state.step = "upload"
# if "quiz" not in st.session_state: st.session_state.quiz = None
# if "answers" not in st.session_state: st.session_state.answers = []
# if "start_time" not in st.session_state: st.session_state.start_time = None
# if "time_limit" not in st.session_state: st.session_state.time_limit = 0

# # -----------------------------
# # 3. PROFESSIONAL TIMER FRAGMENT
# # -----------------------------
# @st.fragment(run_every=1)
# def sync_timer():
#     """Ticking timer that forces submission on zero."""
#     if st.session_state.start_time and st.session_state.step == "quiz":
#         elapsed = int(time.time() - st.session_state.start_time)
#         remaining = st.session_state.time_limit - elapsed
        
#         if remaining <= 0:
#             st.session_state.step = "result"
#             st.rerun()
        
#         mins, secs = divmod(remaining, 60)
#         # Use delta to show a warning color when under 30 seconds
#         color = "normal" if remaining > 30 else "inverse"
#         st.metric("⏳ Time Remaining", f"{mins:02d}:{secs:02d}", delta=f"{remaining}s", delta_color=color)

# # -----------------------------
# # 4. SIDEBAR
# # -----------------------------
# with st.sidebar:
#     st.header("⚙️ Exam Settings")
    
#     if st.session_state.step == "quiz":
#         sync_timer()
#         st.write("---")

#     exam = st.selectbox("Exam", ["BCS", "NTRCA", "Primary"])
#     lang = st.selectbox("Language", ["Bengali", "English", "Arabic"])
#     count = st.slider("Questions", 5, 50, 10)
#     diff = st.select_slider("Difficulty", ["Beginner", "Intermediate", "Expert"])

#     if st.button("Reset System", use_container_width=True):
#         st.session_state.clear()
#         st.rerun()

# # -----------------------------
# # 5. UPLOAD & GENERATE
# # -----------------------------
# if st.session_state.step == "upload":
#     st.subheader(f"🚀 Prepare for {exam} Exam")
#     file = st.file_uploader("Upload Study Material (PDF/Image)", ["pdf", "jpg", "jpeg", "png"])

#     if st.button("Generate Quiz", use_container_width=True):
#         if not file:
#             st.warning("⚠️ Please upload a file first")
#         else:
#             ext = file.name.split(".")[-1]
#             with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
#                 tmp.write(file.getbuffer())
#                 tmp_path = tmp.name

#             try:
#                 with st.spinner("Analyzing content and generating questions..."):
#                     quiz = engine.generate_quiz(tmp_path, count, diff, lang, exam)
#                     st.session_state.quiz = quiz
#                     st.session_state.answers = [None] * len(quiz)
#                     st.session_state.start_time = time.time()
#                     # Allocation: 30 seconds per question
#                     st.session_state.time_limit = len(quiz) * 30 
#                     st.session_state.step = "quiz"
#                     st.rerun()
#             except Exception as e:
#                 st.error(f"Error: {e}")
#             finally:
#                 if os.path.exists(tmp_path): os.remove(tmp_path)

# # -----------------------------
# # 6. QUIZ MODE
# # -----------------------------
# elif st.session_state.step == "quiz":
#     st.subheader(f"📝 {exam} Practice Mode")

#     with st.form("exam_form"):
#         for i, q in enumerate(st.session_state.quiz):
#             st.markdown(f"""
#                 <div class="question-card">
#                     <b>Question {i+1}</b><br>{q['q']}
#                 </div>
#             """, unsafe_allow_html=True)
            
#             st.session_state.answers[i] = st.radio(
#                 f"Options for Q{i+1}",
#                 q["options"],
#                 key=f"q{i}",
#                 index=None,
#                 label_visibility="collapsed"
#             )
#             st.write("")

#         if st.form_submit_button("Submit Exam", use_container_width=True):
#             st.session_state.step = "result"
#             st.rerun()

# # -----------------------------
# # 7. RESULT & REVIEW
# # -----------------------------
# # -----------------------------
# # 7. STEP: RESULT & REVIEW (STRICT SANITIZATION)
# # -----------------------------
# elif st.session_state.step == "result":
#     total = len(st.session_state.quiz)
#     score = sum(1 for i, q in enumerate(st.session_state.quiz) 
#                 if st.session_state.answers[i] == q["options"][q["correct_idx"]])

#     st.balloons()
    
#     col1, col2 = st.columns([1, 2])
#     with col1:
#         st.markdown(f"### 📊 Score \n # {score}/{total}")
#         accuracy = (score/total)*100
#         acc_color = "#2ecc71" if accuracy >= 70 else "#f1c40f" if accuracy >= 40 else "#ff4b4b"
#         st.markdown(f"<p style='color:{acc_color}; font-size:24px; font-weight:bold;'>↑ {accuracy:.1f}% Accuracy</p>", unsafe_allow_html=True)
#     with col2:
#         st.bar_chart({"Correct": [score], "Wrong": [total - score]}, height=200)

#     st.markdown("---")
#     st.subheader("🔍 Detailed Review")

#     for i, q in enumerate(st.session_state.quiz):
#         user_ans = st.session_state.answers[i]
#         correct_ans = q["options"][q["correct_idx"]]
#         is_correct = (user_ans == correct_ans)
        
#         # --- CRITICAL FIX: RECURSIVE TAG STRIPPING ---
#         # This removes any HTML tags the AI might have baked into the explanation string
#         import re
#         raw_exp = q.get('explanation', 'No explanation available.')
#         # This regex removes ALL HTML tags like <p>, <hr>, <div> etc.
#         clean_exp = re.sub('<[^<]+?>', '', raw_exp) 

#         status_color = "#2ecc71" if is_correct else "#ff4b4b"
#         status_bg = "rgba(46, 204, 113, 0.1)" if is_correct else "rgba(231, 76, 60, 0.1)"
        
#         # Build the HTML block safely
#         review_card = f"""
#         <div style="border-left: 8px solid {status_color}; 
#                     padding: 20px; 
#                     margin-bottom: 25px; 
#                     background-color: {status_bg}; 
#                     border-radius: 10px;">
#             <h4 style="color: {status_color}; margin-top: 0;">Question {i+1}. {q['q']}</h4>
#             <p style="margin: 10px 0; color: white;"><b>Your Answer:</b> {f'<span style="color:{status_color}">{user_ans}</span>' if user_ans else '<span style="color:orange">Skipped</span>'}</p>
#         """
        
#         if not is_correct:
#             review_card += f'<p style="margin: 10px 0; color: white;"><b>Correct Answer:</b> <span style="color:#2ecc71">{correct_ans}</span></p>'
        
#         review_card += f"""
#             <hr style="opacity: 0.2; margin: 15px 0; border: 0.5px solid #ccc;">
#             <p style="font-size: 0.95em; line-height: 1.6; opacity: 0.9; color: white;">
#                 <b>Explanation:</b> {clean_exp}
#             </p>
#         </div>
#         """
#         st.markdown(review_card, unsafe_allow_html=True)

#     if st.button("⬅️ Start New Session", use_container_width=True):
#         st.session_state.clear()
#         st.rerun()







# import datetime
# import streamlit as st
# import os, tempfile, time, json, re
# from dotenv import load_dotenv
# from modules.ai_engine import QuizEngine

# # -----------------------------
# # 1. SETUP & PROFESSIONAL THEME
# # -----------------------------
# load_dotenv()

# def load_assets():
#     st.set_page_config(page_title="EduSmart AI Portal", page_icon="🎓", layout="wide")
#     st.markdown("""
#         <style>
#         /* Main Background */
#         .main { background: #0d1117; color: #c9d1d9; }
        
#         /* Glassmorphism Cards */
#         .stMetric, .question-card, .result-card {
#             background: rgba(22, 27, 34, 0.8);
#             border: 1px solid #30363d;
#             border-radius: 12px;
#             padding: 20px;
#             box-shadow: 0 4px 6px rgba(0,0,0,0.1);
#         }
        
#         /* Custom Question Heading */
#         .q-title {
#             color: #58a6ff;
#             font-size: 1.1em;
#             font-weight: 600;
#             margin-bottom: 8px;
#         }

#         /* Submit Button Styling */
#         div.stButton > button:first-child {
#             background-color: #238636;
#             color: white;
#             border-radius: 8px;
#             border: none;
#             padding: 10px 24px;
#         }
#         </style>
#     """, unsafe_allow_html=True)

# load_assets()
# engine = QuizEngine(os.getenv("GEMINI_API_KEY"))

# # -----------------------------
# # 2. SESSION STATE
# # -----------------------------
# if "step" not in st.session_state: st.session_state.step = "upload"
# if "quiz" not in st.session_state: st.session_state.quiz = None
# if "answers" not in st.session_state: st.session_state.answers = []
# if "start_time" not in st.session_state: st.session_state.start_time = None
# if "time_limit" not in st.session_state: st.session_state.time_limit = 0

# # -----------------------------
# # 3. BACKGROUND TIMER FRAGMENT
# # -----------------------------
# @st.fragment(run_every=1)
# def sync_timer():
#     if st.session_state.start_time and st.session_state.step == "quiz":
#         elapsed = int(time.time() - st.session_state.start_time)
#         remaining = st.session_state.time_limit - elapsed
        
#         if remaining <= 0:
#             st.session_state.step = "result"
#             st.rerun()
        
#         mins, secs = divmod(remaining, 60)
#         color = "normal" if remaining > 30 else "inverse"
#         st.metric("⏳ Time Remaining", f"{mins:02d}:{secs:02d}", delta=f"{remaining}s", delta_color=color)

# # -----------------------------
# # 4. SIDEBAR
# # -----------------------------
# with st.sidebar:
#     st.title("🎓 EduSmart AI")
#     if st.session_state.step == "quiz":
#         sync_timer()
#         st.write("---")

#     exam = st.selectbox("Exam Category", ["BCS", "NTRCA", "Primary", "Bank Job", "Admission"])
#     lang = st.selectbox("Language", ["Bengali", "English"])
#     count = st.slider("Questions", 5, 50, 10)
#     diff = st.select_slider("Difficulty", ["Beginner", "Intermediate", "Expert"])

#     if st.button("🔄 Reset Portal", use_container_width=True):
#         st.session_state.clear()
#         st.rerun()

# # -----------------------------
# # 5. STEP: UPLOAD
# # -----------------------------
# if st.session_state.step == "upload":
#     st.header("🚀 Start Your Assessment")
#     st.write("Upload a photo of a question paper, a PDF note, or a textbook page.")
    
#     file = st.file_uploader("Drop your material here", type=["pdf", "jpg", "jpeg", "png"])

#     if st.button("Generate Exam", use_container_width=True):
#         if not file:
#             st.error("Please upload a source file.")
#         else:
#             with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.name.split('.')[-1]}") as tmp:
#                 tmp.write(file.getbuffer())
#                 tmp_path = tmp.name

#             try:
#                 with st.spinner("🤖 AI analyzing material..."):
#                     quiz_data = engine.generate_quiz(tmp_path, count, diff, lang, exam)
#                     st.session_state.quiz = quiz_data
#                     st.session_state.answers = [None] * len(quiz_data)
#                     st.session_state.start_time = time.time()
#                     st.session_state.time_limit = len(quiz_data) * 45 # 45s per question
#                     st.session_state.step = "quiz"
#                     st.rerun()
#             finally:
#                 if os.path.exists(tmp_path): os.remove(tmp_path)

# # -----------------------------
# # 6. STEP: QUIZ MODE
# # -----------------------------
# elif st.session_state.step == "quiz":
#     st.subheader(f"📝 {exam} Mode | {len(st.session_state.quiz)} Questions")
    
#     with st.form("exam_form"):
#         for i, q in enumerate(st.session_state.quiz):
#             st.markdown(f'''
#                 <div class="question-card">
#                     <div class="q-title">Question {i+1}</div>
#                     {q['q']}
#                 </div>
#             ''', unsafe_allow_html=True)
            
#             st.session_state.answers[i] = st.radio(
#                 f"Options_{i}", q["options"], key=f"q{i}", index=None, label_visibility="collapsed"
#             )
#             st.write("")

#         if st.form_submit_button("Submit Assessment", use_container_width=True):
#             st.session_state.step = "result"
#             st.rerun()

# # -----------------------------
# # 7. STEP: PRO RESULT & ANALYTICS
# # -----------------------------
# elif st.session_state.step == "result":
#     CUT_MARK = 0.25 
#     raw_score = 0
#     wrong_count = 0
#     skipped = 0
    
#     for i, q in enumerate(st.session_state.quiz):
#         if st.session_state.answers[i] == q["options"][q["correct_idx"]]: raw_score += 1
#         elif st.session_state.answers[i] is None: skipped += 1
#         else: wrong_count += 1

#     net_score = raw_score - (wrong_count * CUT_MARK)
#     pass_status = "PASSED" if net_score >= (len(st.session_state.quiz) * 0.4) else "FAILED"
#     status_color = "#238636" if pass_status == "PASSED" else "#da3633"

#     st.balloons()
    
#     # Dashboard Header
#     c1, c2, c3 = st.columns([1, 1, 1])
#     with c1:
#         st.metric("Net Score", f"{net_score:.2f}")
#     with c2:
#         st.markdown(f"<div style='text-align:center; padding:10px; border-radius:10px; background:{status_color}; color:white; font-weight:bold; font-size:20px;'>{pass_status}</div>", unsafe_allow_html=True)
#     with c3:
#         st.metric("Accuracy", f"{(raw_score/len(st.session_state.quiz))*100:.1f}%")

#     st.write("---")
    
#     # Detailed Review Section
#     st.subheader("🔍 Review & Insights")
#     for i, q in enumerate(st.session_state.quiz):
#         u_ans = st.session_state.answers[i]
#         c_ans = q["options"][q["correct_idx"]]
#         is_correct = (u_ans == c_ans)
        
#         # Professional UI for each card
#         clean_exp = re.sub('<[^<]+?>', '', q.get('explanation', ''))
#         card_color = "#238636" if is_correct else "#da3633"
        
#         review_html = f"""
#         <div style="border-left: 5px solid {card_color}; background: rgba(255,255,255,0.03); padding: 15px; border-radius: 8px; margin-bottom: 15px;">
#             <p style="margin:0; font-weight:bold; color:{card_color};">Question {i+1} {"✅" if is_correct else "❌"}</p>
#             <p style="margin: 10px 0;">{q['q']}</p>
#             <p style="font-size: 0.9em;"><b>Your Answer:</b> {u_ans if u_ans else '<span style="color:orange">Skipped</span>'}</p>
#             {f'<p style="font-size: 0.9em;"><b>Correct:</b> {c_ans}</p>' if not is_correct else ""}
#             <p style="font-size: 0.85em; opacity: 0.7; font-style: italic;"><b>AI Insight:</b> {clean_exp}</p>
#         </div>
#         """
#         st.markdown(review_html, unsafe_allow_html=True)

#     if st.button("Take New Exam", use_container_width=True):
#         st.session_state.clear()
#         st.rerun()




# import streamlit as st
# import os, tempfile, time, json, re
# from dotenv import load_dotenv
# # from ai_engine import QuizEngine # Ensure this filename matches your engine file
# from modules.ai_engine import QuizEngine

# # -----------------------------
# # 1. CSS & UI SETUP
# # -----------------------------
# def load_assets():
#     st.set_page_config(page_title="EduSmart AI", page_icon="🎓", layout="wide")
    
#     # Inject External CSS
#     # if os.path.exists("style.css"):
#     if os.path.exists("assets/style.css"):
#         with open("assets/style.css") as f:
#             st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
#     else:
#         st.warning("style.css not found. Using default styles.")

# load_assets()

# # Initialize Engine
# load_dotenv()
# api_key = os.getenv("GEMINI_API_KEY")
# if not api_key:
#     st.error("Missing GEMINI_API_KEY in .env file")
# engine = QuizEngine(api_key)

# # -----------------------------
# # 2. SESSION STATE
# # -----------------------------
# if "step" not in st.session_state: st.session_state.step = "upload"
# if "quiz" not in st.session_state: st.session_state.quiz = None
# if "answers" not in st.session_state: st.session_state.answers = []
# if "start_time" not in st.session_state: st.session_state.start_time = None
# if "time_limit" not in st.session_state: st.session_state.time_limit = 0

# # -----------------------------
# # 3. SIDEBAR & TIMER
# # -----------------------------
# with st.sidebar:
#     st.title("🎓 EduSmart AI")
    
#     # Dynamic Timer Fragment
#     @st.fragment(run_every=1)
#     def show_timer():
#         if st.session_state.step == "quiz" and st.session_state.start_time:
#             elapsed = int(time.time() - st.session_state.start_time)
#             remaining = max(0, st.session_state.time_limit - elapsed)
#             if remaining == 0:
#                 st.session_state.step = "result"
#                 st.rerun()
#             mins, secs = divmod(remaining, 60)
#             st.metric("⏳ Time Left", f"{mins:02d}:{secs:02d}")

#     show_timer()
    
#     exam = st.selectbox("Exam Category", ["BCS", "NTRCA", "Primary", "Bank Job", "Admission"])
#     lang = st.selectbox("Language", ["Bengali", "English"])
#     count = st.slider("Questions", 5, 30, 10)
#     diff = st.select_slider("Difficulty", ["Beginner", "Intermediate", "Expert"])

#     if st.button("🔄 Reset Portal"):
#         st.session_state.clear()
#         st.rerun()

# # -----------------------------
# # 4. APP LOGIC (UPLOAD -> QUIZ -> RESULT)
# # -----------------------------
# if st.session_state.step == "upload":
#     st.header("🚀 Start Your Assessment")
#     file = st.file_uploader("Upload Question Paper (PDF/Image)", type=["pdf", "jpg", "png"])

#     if st.button("Generate Exam", use_container_width=True):
#         if file:
#             with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.name.split('.')[-1]}") as tmp:
#                 tmp.write(file.getbuffer())
#                 tmp_path = tmp.name

#             try:
#                 with st.spinner("🤖 AI is analyzing your document using fallback models..."):
#                     quiz_data = engine.generate_quiz(tmp_path, count, diff, lang, exam)
#                     st.session_state.quiz = quiz_data
#                     st.session_state.answers = [None] * len(quiz_data)
#                     st.session_state.start_time = time.time()
#                     st.session_state.time_limit = len(quiz_data) * 60 
#                     st.session_state.step = "quiz"
#                     st.rerun()
#             except Exception as e:
#                 st.error(f"Error: {e}")
#             finally:
#                 if os.path.exists(tmp_path): os.remove(tmp_path)

# elif st.session_state.step == "quiz":
#     st.subheader(f"📝 {exam} Quiz")
    
#     with st.form("quiz_form"):
#         for i, q in enumerate(st.session_state.quiz):
#             st.markdown(f'<div class="question-card"><b>Q{i+1}:</b> {q["q"]}</div>', unsafe_allow_html=True)
#             st.session_state.answers[i] = st.radio(f"Select Answer {i}", q["options"], key=f"ans_{i}", label_visibility="collapsed")
        
#         if st.form_submit_button("Finish Exam"):
#             st.session_state.step = "result"
#             st.rerun()

# elif st.session_state.step == "result":
#     st.header("📊 Your Results")
#     # Logic for scoring (matching your original logic)
#     correct = sum(1 for i, q in enumerate(st.session_state.quiz) if st.session_state.answers[i] == q["options"][q["correct_idx"]])
#     st.success(f"You got {correct} out of {len(st.session_state.quiz)} correct!")
    
#     if st.button("Try Another"):
#         st.session_state.clear()
#         st.rerun()










# import streamlit as st
# import os, tempfile, time, json, re
# from dotenv import load_dotenv
# from modules.ai_engine import QuizEngine

# # -----------------------------
# # 1. UI SETUP & ASSETS
# # -----------------------------
# def load_assets():
#     st.set_page_config(page_title="EduSmart AI", page_icon="🎓", layout="wide")
    
#     # Inject External CSS from assets folder
#     if os.path.exists("assets/style.css"):
#         with open("assets/style.css") as f:
#             st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
#     else:
#         st.info("💡 Tip: Add assets/style.css to customize the look of your app.")

#     # Map categories to Streamlit-supported divider colors
#     return {
#         "BCS": "red", 
#         "NTRCA": "blue", 
#         "Primary": "green", 
#         "Bank Job": "orange", 
#         "Admission": "violet"
#     }

# supported_colors = load_assets()

# # Initialize Engine with Environment Variables
# load_dotenv()
# api_key = os.getenv("GEMINI_API_KEY")
# if not api_key:
#     st.error("Missing GEMINI_API_KEY in .env file. Please add your key to proceed.")
#     st.stop()

# engine = QuizEngine(api_key)

# # -----------------------------
# # 2. SESSION STATE MANAGEMENT
# # -----------------------------
# if "step" not in st.session_state: st.session_state.step = "upload"
# if "quiz" not in st.session_state: st.session_state.quiz = None
# if "answers" not in st.session_state: st.session_state.answers = []
# if "start_time" not in st.session_state: st.session_state.start_time = None
# if "time_limit" not in st.session_state: st.session_state.time_limit = 0

# # -----------------------------
# # 3. SIDEBAR & SETTINGS
# # -----------------------------
# with st.sidebar:
#     st.title("🎓 EduSmart AI")
    
#     # Real-time Countdown Timer
#     @st.fragment(run_every=1)
#     def show_timer():
#         if st.session_state.step == "quiz" and st.session_state.start_time:
#             elapsed = int(time.time() - st.session_state.start_time)
#             remaining = max(0, st.session_state.time_limit - elapsed)
#             if remaining == 0:
#                 st.session_state.step = "result"
#                 st.rerun()
#             mins, secs = divmod(remaining, 60)
#             st.metric("⏳ Time Remaining", f"{mins:02d}:{secs:02d}")

#     show_timer()
    
#     # Quiz Configuration
#     exam = st.selectbox("Exam Category", list(supported_colors.keys()))
#     lang = st.selectbox("Language", ["Bengali","English"])
#     count = st.slider("Number of Questions", 5, 30, 10)
#     diff = st.select_slider("Difficulty Level", ["Beginner", "Intermediate", "Expert"])

#     if st.button("🔄 Reset Portal", use_container_width=True):
#         st.session_state.clear()
#         st.rerun()

# # Determine current theme color based on sidebar selection
# theme_color = supported_colors.get(exam, "gray")

# # -----------------------------
# # 4. MAIN APP LOGIC
# # -----------------------------

# # --- STEP 1: UPLOAD PHASE ---
# if st.session_state.step == "upload":
#     # The header changes dynamically based on the 'exam' variable
#     st.header(f"🚀 Start Your {exam} Assessment", divider=theme_color)
    
#     file = st.file_uploader(f"Upload {exam} Study Material (PDF or Image)", type=["pdf", "jpg", "png"])

#     if st.button("Generate Exam", use_container_width=True, type="primary"):
#         if file:
#             with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.name.split('.')[-1]}") as tmp:
#                 tmp.write(file.getbuffer())
#                 tmp_path = tmp.name

#             try:
#                 with st.spinner(f"🤖 AI is analyzing your {exam} document..."):
#                     quiz_data = engine.generate_quiz(tmp_path, count, diff, lang, exam)
                    
#                     # Store quiz and initialize answers list based on question count
#                     st.session_state.quiz = quiz_data
#                     st.session_state.answers = [None] * len(quiz_data)
#                     st.session_state.start_time = time.time()
#                     st.session_state.time_limit = len(quiz_data) * 60  # 1 minute per question
#                     st.session_state.step = "quiz"
#                     st.rerun()
#             except Exception as e:
#                 st.error(f"Failed to generate quiz: {e}")
#             finally:
#                 if os.path.exists(tmp_path): os.remove(tmp_path)
#         else:
#             st.warning("Please upload a file before clicking generate.")

# # --- STEP 2: LIVE QUIZ PHASE ---
# elif st.session_state.step == "quiz":
#     st.subheader(f"📝 {exam} Live Exam ({diff} Level)", divider=theme_color)
    
#     with st.form("quiz_form"):
#         # This loop automatically adjusts whether there are 5 or 30 questions
#         for i, q in enumerate(st.session_state.quiz):
#             st.markdown(f"**Question {i+1}:** {q['q']}")
#             st.session_state.answers[i] = st.radio(
#                 f"Options for Q{i+1}", 
#                 q["options"], 
#                 key=f"ans_{i}", 
#                 label_visibility="collapsed",
#                 index=None
#             )
#             st.divider()
        
#         if st.form_submit_button("Submit and Finish Exam", use_container_width=True):
#             st.session_state.step = "result"
#             st.rerun()

# # --- STEP 3: RESULTS & REVIEW PHASE ---
# elif st.session_state.step == "result":
#     # Dynamic header based on the selected exam category
#     st.header(f"📊 {exam} Performance Report", divider=theme_color)
    
#     # 1. Scoring Logic
#     total_q = len(st.session_state.quiz)
#     correct_count = sum(1 for i, q in enumerate(st.session_state.quiz) 
#                        if st.session_state.answers[i] == q["options"][q["correct_idx"]])
    
#     score_pct = (correct_count / total_q) * 100
    
#     # 2. Visual Metrics
#     col1, col2, col3 = st.columns(3)
#     col1.metric("Correct Answers", f"{correct_count} / {total_q}")
#     col2.metric("Accuracy", f"{score_pct:.1f}%")
    
#     # Calculate time taken if start_time exists
#     if st.session_state.start_time:
#         duration = int(time.time() - st.session_state.start_time)
#         mins, secs = divmod(duration, 60)
#         col3.metric("Time Taken", f"{mins:02d}:{secs:02d}")

#     # 3. Encouragement Logic
#     if score_pct >= 80:
#         st.balloons()
#         st.success("✨ **Mastery Achieved!** You are well-prepared for the actual exam. Focus on maintaining this speed.")
#     elif score_pct >= 50:
#         st.info("👍 **Good Progress!** You have a solid foundation. Review the questions you missed to reach 100%.")
#     else:
#         st.warning("⚠️ **Keep Practicing!** Don't be discouraged. Use the review section below to understand your mistakes and try again.")

#     st.divider()
    
#     # 4. The Detailed Review Section
#     st.subheader("🔍 Question-by-Question Review")
#     st.caption("Click on a question to see the correct answer and AI explanation.")

#     for i, q in enumerate(st.session_state.quiz):
#         user_choice = st.session_state.answers[i]
#         correct_choice = q["options"][q["correct_idx"]]
#         is_correct = (user_choice == correct_choice)
        
#         # Color coding the expander label
#         label = f"Question {i+1}: {'✅ Correct' if is_correct else '❌ Incorrect'}"
        
#         with st.expander(label):
#             st.write(f"**Question:** {q['q']}")
            
#             # Show the comparison
#             c1, c2 = st.columns(2)
#             with c1:
#                 st.markdown(f"**Your Answer:** \n:{'green' if is_correct else 'red'}[{user_choice}]")
#             with c2:
#                 if not is_correct:
#                     st.markdown(f"**Correct Answer:** \n:green[{correct_choice}]")
#                 else:
#                     st.write("✨ Spot on!")

#             # 5. The Learning Part: Explanation
#             st.info(f"**Expert Explanation:** {q.get('explanation', 'No detailed explanation available for this question.')}")

#     # 6. Navigation
#     st.divider()
#     if st.button("🏁 Take a New Assessment", use_container_width=True):
#         st.session_state.clear()
#         st.rerun()








# import streamlit as st
# import os, tempfile, time, json
# from dotenv import load_dotenv
# from modules.ai_engine import QuizEngine

# # -----------------------------
# # 1. UI SETUP & ASSETS
# # -----------------------------
# def load_assets():
#     st.set_page_config(page_title="EduSmart AI", page_icon="🎓", layout="wide")
#     if os.path.exists("assets/style.css"):
#         with open("assets/style.css") as f:
#             st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

#     return {
#         "BCS": "red", "NTRCA": "blue", "Primary": "green", 
#         "Bank Job": "orange", "Admission": "violet"
#     }

# supported_colors = load_assets()

# # Initialize Engine
# load_dotenv()
# api_key = os.getenv("GEMINI_API_KEY")
# if not api_key:
#     st.error("Missing GEMINI_API_KEY in .env file.")
#     st.stop()

# engine = QuizEngine(api_key)

# # -----------------------------
# # 2. SESSION STATE
# # -----------------------------
# if "step" not in st.session_state: st.session_state.step = "upload"
# if "quiz" not in st.session_state: st.session_state.quiz = None
# if "answers" not in st.session_state: st.session_state.answers = []
# if "start_time" not in st.session_state: st.session_state.start_time = None
# if "time_limit" not in st.session_state: st.session_state.time_limit = 0

# # -----------------------------
# # 3. SIDEBAR
# # -----------------------------
# with st.sidebar:
#     st.title("🎓 EduSmart AI")
    
#     @st.fragment(run_every=1)
#     def show_timer():
#         if st.session_state.step == "quiz" and st.session_state.start_time:
#             elapsed = int(time.time() - st.session_state.start_time)
#             remaining = max(0, st.session_state.time_limit - elapsed)
#             if remaining == 0:
#                 st.session_state.step = "result"
#                 st.rerun()
#             mins, secs = divmod(remaining, 60)
#             st.metric("⏳ Time Remaining", f"{mins:02d}:{secs:02d}")

#     show_timer()
    
#     exam = st.selectbox("Exam Category", list(supported_colors.keys()))
#     lang = st.selectbox("Language", ["Bengali","English"])
#     count = st.slider("Number of Questions", 5, 30, 10)
#     diff = st.select_slider("Difficulty Level", ["Beginner", "Intermediate", "Expert"])

#     if st.button("🔄 Reset Portal", use_container_width=True):
#         st.session_state.clear()
#         st.rerun()

# theme_color = supported_colors.get(exam, "gray")

# # -----------------------------
# # 4. MAIN LOGIC
# # -----------------------------

# # STEP 1: UPLOAD
# if st.session_state.step == "upload":
#     st.header(f"🚀 Start Your {exam} Assessment", divider=theme_color)
#     file = st.file_uploader(f"Upload {exam} paper (PDF/Image)", type=["pdf", "jpg", "png"])

#     if st.button("Generate Exam", use_container_width=True, type="primary"):
#         if file:
#             with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.name.split('.')[-1]}") as tmp:
#                 tmp.write(file.getbuffer())
#                 tmp_path = tmp.name

#             try:
#                 with st.spinner(f"🤖 AI specialized for {exam} is analyzing your document..."):
#                     quiz_data = engine.generate_quiz(tmp_path, count, diff, lang, exam)
#                     st.session_state.quiz = quiz_data
#                     st.session_state.answers = [None] * len(quiz_data)
#                     st.session_state.start_time = time.time()
#                     st.session_state.time_limit = len(quiz_data) * 30 
#                     st.session_state.step = "quiz"
#                     st.rerun()
#             except Exception as e:
#                 st.error(f"Error: {e}")
#             finally:
#                 if os.path.exists(tmp_path): os.remove(tmp_path)

# # STEP 2: QUIZ
# elif st.session_state.step == "quiz":
#     st.subheader(f"📝 {exam} Quiz Mode", divider=theme_color)
#     with st.form("quiz_form"):
#         for i, q in enumerate(st.session_state.quiz):
#             st.markdown(f"**Q{i+1}:** {q['q']}")
#             st.session_state.answers[i] = st.radio(
#                 f"Options for Q{i+1}", q["options"], key=f"ans_{i}", label_visibility="collapsed", index=None
#             )
#             st.divider()
#         if st.form_submit_button("Finish Exam", use_container_width=True):
#             st.session_state.step = "result"
#             st.rerun()

# # STEP 3: RESULT
# elif st.session_state.step == "result":
#     st.header(f"📊 {exam} Results", divider=theme_color)
    
#     total_q = len(st.session_state.quiz)
#     correct_count = sum(1 for i, q in enumerate(st.session_state.quiz) 
#                        if st.session_state.answers[i] == q["options"][q["correct_idx"]])
    
#     score_pct = (correct_count / total_q) * 100
    
#     # Metrics
#     c1, c2, c3 = st.columns(3)
#     c1.metric("Score", f"{correct_count}/{total_q}")
#     c2.metric("Accuracy", f"{score_pct:.1f}%")
#     if st.session_state.start_time:
#         dur = int(time.time() - st.session_state.start_time)
#         m, s = divmod(dur, 60)
#         c3.metric("Time", f"{m:02d}:{s:02d}")

#     # Review Section
#     st.divider()
#     st.subheader("🔍 Review Mistakes & Explanations")
#     for i, q in enumerate(st.session_state.quiz):
#         u_ans = st.session_state.answers[i]
#         c_ans = q["options"][q["correct_idx"]]
#         is_ok = (u_ans == c_ans)
        
#         with st.expander(f"Q{i+1}: {'✅' if is_ok else '❌'} {q['q'][:50]}..."):
#             st.write(f"**Full Question:** {q['q']}")
#             st.markdown(f"**Your Answer:** :{'green' if is_ok else 'red'}[{u_ans}]")
#             if not is_ok: st.markdown(f"**Correct Answer:** :green[{c_ans}]")
#             st.info(f"**Explanation:** {q.get('explanation', 'N/A')}")

#     if st.button("🏁 Restart Assessment", use_container_width=True):
#         st.session_state.clear()
#         st.rerun()



import streamlit as st
import os, tempfile, time, json
from dotenv import load_dotenv
from modules.ai_engine import QuizEngine

# -----------------------------
# 1. UI SETUP & ASSETS
# -----------------------------
def load_assets():
    st.set_page_config(page_title="EduSmart AI", page_icon="🎓", layout="wide")
    if os.path.exists("assets/style.css"):
        with open("assets/style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    return {
        "BCS": "red", "NTRCA": "blue", "Primary": "green", 
        "Bank Job": "orange", "Admission": "violet"
    }

supported_colors = load_assets()

# Initialize Engine
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("Missing GEMINI_API_KEY in .env file.")
    st.stop()

engine = QuizEngine(api_key)

# -----------------------------
# 2. SESSION STATE
# -----------------------------
if "step" not in st.session_state: st.session_state.step = "upload"
if "quiz" not in st.session_state: st.session_state.quiz = None
if "answers" not in st.session_state: st.session_state.answers = []
if "start_time" not in st.session_state: st.session_state.start_time = None
if "time_limit" not in st.session_state: st.session_state.time_limit = 0

# -----------------------------
# 3. SIDEBAR
# -----------------------------
with st.sidebar:
    st.title("🎓 EduSmart AI")
    
    @st.fragment(run_every=1)
    def show_timer():
        if st.session_state.step == "quiz" and st.session_state.start_time:
            elapsed = int(time.time() - st.session_state.start_time)
            remaining = max(0, st.session_state.time_limit - elapsed)
            if remaining == 0:
                st.session_state.step = "result"
                st.rerun()
            mins, secs = divmod(remaining, 60)
            st.metric("⏳ Time Remaining", f"{mins:02d}:{secs:02d}")

    show_timer()
    
    exam = st.selectbox("Exam Category", list(supported_colors.keys()))
    lang = st.selectbox("Language", ["Bengali","English"])
    count = st.slider("Number of Questions", 5, 30, 10)
    diff = st.select_slider("Difficulty Level", ["Beginner", "Intermediate", "Expert"])

    if st.button("🔄 Reset Portal", use_container_width=True):
        st.session_state.clear()
        st.rerun()

theme_color = supported_colors.get(exam, "gray")

# -----------------------------
# 4. MAIN LOGIC
# -----------------------------

# STEP 1: UPLOAD
if st.session_state.step == "upload":
    st.header(f"🚀 Start Your {exam} Assessment", divider=theme_color)
    file = st.file_uploader(f"Upload {exam} paper (PDF/Image)", type=["pdf", "jpg", "png"])

    if st.button("Generate Exam", use_container_width=True, type="primary"):
        if file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.name.split('.')[-1]}") as tmp:
                tmp.write(file.getbuffer())
                tmp_path = tmp.name

            # --- SPINNER & STATUS LOGIC START ---
            with st.spinner(f"🤖 AI specialized for {exam} is working..."):
                status_placeholder = st.empty()
                try:
                    status_placeholder.info("📡 Connecting to AI specialized engine...")
                    
                    # Call the engine
                    quiz_data = engine.generate_quiz(tmp_path, count, diff, lang, exam)
                    
                    status_placeholder.success("✅ Quiz generated successfully!")
                    time.sleep(1) # Brief pause so user sees the success message
                    
                    st.session_state.quiz = quiz_data
                    st.session_state.answers = [None] * len(quiz_data)
                    st.session_state.start_time = time.time()
                    st.session_state.time_limit = len(quiz_data) * 60 # Set to 60s per question
                    st.session_state.step = "quiz"
                    st.rerun()
                    
                except Exception as e:
                    status_placeholder.empty()
                    st.error(f"❌ Error during generation: {e}")
                finally:
                    if os.path.exists(tmp_path): 
                        os.remove(tmp_path)
            # --- SPINNER & STATUS LOGIC END ---
        else:
            st.warning("⚠️ Please upload a file first!")

# STEP 2: QUIZ
elif st.session_state.step == "quiz":
    st.subheader(f"📝 {exam} Quiz Mode", divider=theme_color)
    with st.form("quiz_form"):
        for i, q in enumerate(st.session_state.quiz):
            st.markdown(f"**Q{i+1}:** {q['q']}")
            st.session_state.answers[i] = st.radio(
                f"Options for Q{i+1}", q["options"], key=f"ans_{i}", label_visibility="collapsed", index=None
            )
            st.divider()
        if st.form_submit_button("Finish Exam", use_container_width=True):
            st.session_state.step = "result"
            st.rerun()

# STEP 3: RESULT
elif st.session_state.step == "result":
    st.header(f"📊 {exam} Results", divider=theme_color)
    
    total_q = len(st.session_state.quiz)
    correct_count = sum(1 for i, q in enumerate(st.session_state.quiz) 
                       if st.session_state.answers[i] == q["options"][q["correct_idx"]])
    
    score_pct = (correct_count / total_q) * 100
    
    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Score", f"{correct_count}/{total_q}")
    c2.metric("Accuracy", f"{score_pct:.1f}%")
    if st.session_state.start_time:
        dur = int(time.time() - st.session_state.start_time)
        m, s = divmod(dur, 60)
        c3.metric("Time", f"{m:02d}:{s:02d}")

    # Review Section
    st.divider()
    st.subheader("🔍 Review Mistakes & Explanations")
    for i, q in enumerate(st.session_state.quiz):
        u_ans = st.session_state.answers[i]
        c_ans = q["options"][q["correct_idx"]]
        is_ok = (u_ans == c_ans)
        
        with st.expander(f"Q{i+1}: {'✅' if is_ok else '❌'} {q['q'][:50]}..."):
            st.write(f"**Full Question:** {q['q']}")
            st.markdown(f"**Your Answer:** :{'green' if is_ok else 'red'}[{u_ans}]")
            if not is_ok: st.markdown(f"**Correct Answer:** :green[{c_ans}]")
            st.info(f"**Explanation:** {q.get('explanation', 'N/A')}")

    if st.button("🏁 Restart Assessment", use_container_width=True):
        st.session_state.clear()
        st.rerun()
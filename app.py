import streamlit as st
import os
import json
import tempfile
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IELTS 스피킹 영상 메이커",
    page_icon="🎙️",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.question-card {
    background: #f8f6f1;
    border-left: 3px solid #c4956a;
    padding: 16px 20px;
    border-radius: 0 8px 8px 0;
    margin: 12px 0;
    font-size: 15px;
    line-height: 1.6;
}
.answer-box {
    background: #eef4fb;
    border: 1px solid #b8d4ee;
    padding: 16px 20px;
    border-radius: 8px;
    margin: 12px 0;
    font-size: 14px;
    line-height: 1.8;
    font-family: 'DM Mono', monospace;
}
.step-header {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #888;
    margin-bottom: 6px;
}
.voice-card {
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.divider { border: none; border-top: 1px solid #eee; margin: 28px 0; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🎙️ IELTS 스피킹 영상 메이커")
st.markdown("한글 답변 → IELTS 영어 스크립트 → **내 목소리** 영상")
st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Score descriptions ────────────────────────────────────────────────────────
score_desc = {
    5.0: "기초 - 단순 문장, 기본 어휘",
    5.5: "초중급 - 조금 더 자연스럽게",
    6.0: "중급 - 복잡한 구조 시작",
    6.5: "중상급 - 다양한 어휘, 자연스러운 흐름",
    7.0: "상급 - 관용구, 고급 어휘 포함",
    7.5: "고급 - 원어민에 가까운 표현",
    8.0: "최고급 - 네이티브 수준",
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ 설정")

    st.markdown("### 🔑 API Key (Gemini)")
    default_key = ""
    if hasattr(st, "secrets"):
        default_key = st.secrets.get("GEMINI_API_KEY", "")
    user_api_key = st.text_input(
        "Gemini API Key (선택)",
        type="password",
        placeholder="비워두면 기본 키 사용",
        help="aistudio.google.com에서 무료 발급 가능"
    )
    gemini_api_key = user_api_key.strip() if user_api_key.strip() else default_key

    if user_api_key.strip():
        st.caption("✅ 내 API 키 사용 중")
    elif default_key:
        st.caption("✅ 기본 키(Secrets) 사용 중")
    else:
        st.warning("API Key가 없습니다.")
        st.markdown("[무료 발급 →](https://aistudio.google.com/apikey)  카드 불필요")

    st.markdown("---")

    st.markdown("### 🎯 IELTS 목표 점수")
    target_score = st.select_slider(
        "Band Score",
        options=[5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0],
        value=6.5
    )
    st.caption(score_desc[target_score])

    st.markdown("---")

    st.markdown("### 🎬 영상 배경")
    video_style = st.selectbox("스타일", ["다크 미니멀", "라이트 클린", "딥 블루"])
    show_korean = st.checkbox("한글 번역 표시", value=True)

# ── Gemini API 호출 함수 ────────────────────────────────────────────────────
def call_gemini(prompt: str, api_key: str) -> str:
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# ── IELTS 질문 목록 ───────────────────────────────────────────────────────────
QUESTION_BANK = {
    "Part 1 - 일상": [
        "Tell me about your hometown. What do you like most about it?",
        "Do you enjoy cooking? Why or why not?",
        "How do you usually spend your weekends?",
    ],
    "Part 1 - 취미/관심사": [
        "What hobbies do you have?",
        "Do you enjoy reading books? What kind?",
        "How often do you exercise?",
    ],
    "Part 2 - 사람": [
        "Describe a person who has had a great influence on your life.",
        "Describe someone you admire. Who is this person and why do you admire them?",
    ],
    "Part 2 - 경험": [
        "Describe a memorable trip you have taken.",
        "Describe a time when you helped someone.",
    ],
    "Part 3 - 사회/교육": [
        "Do you think technology has improved education? In what ways?",
        "How important is it for young people to learn a second language?",
    ],
}

# ── Session state 초기화 ──────────────────────────────────────────────────────
for key in ["english_script", "korean_translation", "band_tips", "current_question"]:
    if key not in st.session_state:
        st.session_state[key] = ""

# ─────────────────────────────────────────────────────────────────────────────
# Step 1: 질문 선택
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<p class="step-header">Step 1 — 질문 선택</p>', unsafe_allow_html=True)
col1, col2 = st.columns([1, 1])
with col1:
    part = st.selectbox("파트 선택", list(QUESTION_BANK.keys()))
with col2:
    question_mode = st.radio("방식", ["AI가 생성", "랜덤 질문", "직접 입력"])

if question_mode == "AI가 생성":
    if st.button("✨ 새로운 질문 생성", use_container_width=True):
        if not gemini_api_key:
            st.error("API Key가 필요합니다.")
        else:
            with st.spinner("AI 질문 생성 중..."):
                q_prompt = f"Ask ONE random IELTS speaking question for {part}. Return only the question."
                st.session_state.current_question = call_gemini(q_prompt, gemini_api_key)
    question = st.session_state.get("current_question", "질문을 생성해주세요.")
    st.markdown(f'<div class="question-card">❓ {question}</div>', unsafe_allow_html=True)

elif question_mode == "랜덤 질문":
    if st.button("🎲 질문 뽑기", use_container_width=True):
        import random
        st.session_state.current_question = random.choice(QUESTION_BANK[part])
    question = st.session_state.get("current_question", QUESTION_BANK[part][0])
    st.markdown(f'<div class="question-card">❓ {question}</div>', unsafe_allow_html=True)
else:
    question = st.text_area("질문 입력", placeholder="영어 질문을 입력하세요.")

# ─────────────────────────────────────────────────────────────────────────────
# Step 2: 한글 답변
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown('<p class="step-header">Step 2 — 한글로 내 스토리 답변</p>', unsafe_allow_html=True)

korean_answer = st.text_area(
    "한글 답변",
    placeholder="예) 저는 부산 출신인데요, 바다가 가까워서 정말 좋아요. 주말마다 해운대 갔던 기억이 있어요...",
    height=140,
    label_visibility="collapsed"
)

# ─────────────────────────────────────────────────────────────────────────────
# Step 3: AI 영어 스크립트 생성
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown('<p class="step-header">Step 3 — AI 영어 스크립트 생성 (Gemini)</p>', unsafe_allow_html=True)

if st.button("✨ 영어 스크립트 생성", type="primary", use_container_width=True):
    if not gemini_api_key:
        st.error("API Key가 필요합니다. 사이드바에서 설정해주세요.")
    elif not question or question == "질문을 생성해주세요.":
        st.error("질문을 선택하거나 입력해주세요.")
    elif not korean_answer.strip():
        st.error("한글 답변을 입력해주세요.")
    else:
        with st.spinner("Gemini가 스크립트를 작성하는 중..."):
            try:
                prompt = f"""You are an IELTS speaking coach. Transform the Korean answer into natural English for IELTS Band {target_score}.

Band {target_score} guidance: {score_desc[target_score]}

Rules:
- Vocabulary and grammar complexity appropriate for Band {target_score}
- Natural and conversational, not robotic
- Length: 60-120 words for Part 1, 150-200 for Part 2, 80-120 for Part 3
- Use discourse markers (Well, Actually, To be honest, etc.)
- Include personal anecdotes from the Korean input

IELTS Question: {question}
Korean answer: {korean_answer}

Respond ONLY with a raw JSON object - no markdown fences, no extra text:
{{"english": "...", "korean": "자연스러운 한국어 번역", "band_tips": "이 수준에서 사용된 특징적 표현 설명 (한국어)"}}"""

                raw = call_gemini(prompt, gemini_api_key)

                # JSON 펜스 제거
                if "```" in raw:
                    raw = raw.split("```")[1]
                    if raw.startswith("json"):
                        raw = raw[4:]
                start = raw.find("{")
                end = raw.rfind("}") + 1
                raw = raw[start:end]

                data = json.loads(raw)
                st.session_state.english_script = data["english"]
                st.session_state.korean_translation = data["korean"]
                st.session_state.band_tips = data.get("band_tips", "")

            except json.JSONDecodeError:
                st.error("응답 파싱 오류입니다. 다시 시도해주세요.")
            except Exception as e:
                st.error(f"오류: {e}")

english_script = st.session_state.english_script
korean_translation = st.session_state.korean_translation

if english_script:
    st.markdown(f'<div class="answer-box">🇬🇧 {english_script}</div>', unsafe_allow_html=True)

    if show_korean and korean_translation:
        with st.expander("📖 한국어 번역 보기"):
            st.write(korean_translation)

    if st.session_state.get("band_tips"):
        with st.expander("💡 Band 포인트 — 이 표현이 왜 좋은가"):
            st.info(st.session_state.band_tips)

    edited = st.text_area("✏️ 스크립트 수정 (선택)", value=english_script, height=120)
    if edited != english_script:
        st.session_state.english_script = edited
        english_script = edited

# ─────────────────────────────────────────────────────────────────────────────
# Step 4: 목소리 설정
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown('<p class="step-header">Step 4 — 목소리 설정</p>', unsafe_allow_html=True)

voice_tab1, voice_tab2 = st.tabs([
    "🔵 기본 목소리 (gTTS · 무료)",
    "🟢 내 목소리 클로닝 (Chatterbox · 무료)"
])

with voice_tab1:
    st.markdown("""
    <div class="voice-card">
    <b>gTTS (Google Text-to-Speech)</b><br>
    <small>별도 설치 불필요. 인터넷 연결만 있으면 즉시 사용 가능.</small>
    </div>
    """, unsafe_allow_html=True)
    gtts_accent = st.selectbox("영어 억양", ["미국 영어", "영국 영어", "호주 영어"])
    accent_map = {"미국 영어": "en", "영국 영어": "en-GB", "호주 영어": "en-AU"}
    st.session_state.voice_mode = "gtts"
    st.session_state.gtts_lang = accent_map[gtts_accent]

with voice_tab2:
    st.markdown("""
    <div class="voice-card">
    <b>Chatterbox TTS</b> — MIT 라이선스 · 완전 무료<br>
    <small>10초 녹음만으로 내 목소리 복제 · 23개 언어 지원 · GPU 없어도 동작 (느릴 수 있음)</small>
    </div>
    """, unsafe_allow_html=True)

    chatterbox_ready = False
    try:
        from chatterbox.tts import ChatterboxTTS
        chatterbox_ready = True
        st.success("✅ Chatterbox 설치 확인됨")
    except ImportError:
        st.warning("⚠️ Chatterbox가 설치되지 않았습니다.")
        st.code("pip install chatterbox-tts", language="bash")
        st.caption("설치 후 앱을 재시작하세요. Python 3.11 권장.")

    st.caption("10초 이상 · 조용한 환경 · 또박또박 발음 · MP3/WAV")
    ref_audio = st.file_uploader(
        "목소리 파일 업로드",
        type=["mp3", "wav", "m4a"],
        label_visibility="collapsed"
    )

    if ref_audio:
        st.audio(ref_audio)
        st.session_state.ref_audio_bytes = ref_audio.read()
        st.session_state.ref_audio_name = ref_audio.name
        st.success("✅ 녹음 파일 업로드 완료")

    if chatterbox_ready and ref_audio:
        st.session_state.voice_mode = "chatterbox"
        st.info("내 목소리로 영상이 생성됩니다.")
    elif chatterbox_ready and not ref_audio:
        st.caption("파일을 업로드하면 자동으로 내 목소리 모드로 전환됩니다.")

    with st.expander("📝 녹음 팁 — ChatGPT에게 이렇게 부탁하세요"):
        st.markdown("""
> "10초 분량의 자연스러운 영어 문장을 만들어줘. 다양한 발음이 들어가면 좋겠어."

받은 문장을 **조용한 방**에서 스마트폰 녹음 앱으로 읽으세요.
- 너무 빠르거나 느리지 않게
- 문장 끝을 흐리지 않게
- 배경 소음 최소화
        """)

# ─────────────────────────────────────────────────────────────────────────────
# Step 5: 영상 생성
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown('<p class="step-header">Step 5 — 영상 생성</p>', unsafe_allow_html=True)

if not english_script:
    st.info("먼저 Step 3에서 영어 스크립트를 생성해주세요.")
else:
    voice_mode = st.session_state.get("voice_mode", "gtts")
    voice_label = "내 목소리 (Chatterbox)" if voice_mode == "chatterbox" else "기본 TTS (gTTS)"
    st.caption(f"현재 목소리: {voice_label}")

    if st.button("🎬 영상 생성 시작", type="primary", use_container_width=True):
        with st.spinner("영상 제작 중... (목소리에 따라 1~5분 소요)"):
            try:
                from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips

                progress = st.progress(0)
                status = st.empty()
                tmpdir = tempfile.mkdtemp()

                q_audio_path = os.path.join(tmpdir, "question.wav")
                a_audio_path = os.path.join(tmpdir, "answer.wav")

                # ── 음성 생성 ─────────────────────────────────────────────────
                if voice_mode == "chatterbox" and st.session_state.get("ref_audio_bytes"):
                    status.text("🎙️ 내 목소리 생성 중 (Chatterbox)...")
                    progress.progress(10)
                    import torchaudio

                    ref_ext = Path(st.session_state.ref_audio_name).suffix
                    ref_path = os.path.join(tmpdir, f"ref{ref_ext}")
                    with open(ref_path, "wb") as f:
                        f.write(st.session_state.ref_audio_bytes)

                    @st.cache_resource
                    def load_chatterbox():
                        from chatterbox.tts import ChatterboxTTS
                        return ChatterboxTTS.from_pretrained(device="cpu")

                    cb = load_chatterbox()
                    progress.progress(25)

                    status.text("🔊 질문 음성 생성 중...")
                    torchaudio.save(q_audio_path, cb.generate(question, audio_prompt_path=ref_path), cb.sr)
                    progress.progress(45)

                    status.text("🔊 답변 음성 생성 중...")
                    torchaudio.save(a_audio_path, cb.generate(english_script, audio_prompt_path=ref_path), cb.sr)
                    progress.progress(60)

                else:
                    from gtts import gTTS
                    status.text("🔊 음성 생성 중 (gTTS)...")
                    progress.progress(15)
                    gTTS(text=question, lang="en", slow=False).save(q_audio_path)
                    gTTS(text=english_script, lang="en", slow=False).save(a_audio_path)
                    progress.progress(40)

                # ── 배경 프레임 생성 ──────────────────────────────────────────
                status.text("🖼️ 배경 생성 중...")
                W, H = 1280, 720

                def make_frame(style, label, text):
                    img = Image.new("RGB", (W, H))
                    draw = ImageDraw.Draw(img)
                    palettes = {
                        "다크 미니멀": ((15, 15, 25),    (196, 149, 106), (235, 235, 235), (150, 150, 160)),
                        "라이트 클린": ((248, 246, 241),  (70, 90, 160),   (30, 30, 40),   (120, 120, 130)),
                        "딥 블루":     ((10, 30, 60),     (100, 180, 255), (230, 240, 255), (140, 170, 210)),
                    }
                    bg, accent, fg, muted = palettes.get(style, palettes["다크 미니멀"])
                    draw.rectangle([0, 0, W, H], fill=bg)
                    draw.rectangle([60, 80, 80, H - 80], fill=accent)
                    try:
                        fB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
                        fM = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
                        fS = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
                    except Exception:
                        fB = fM = fS = ImageFont.load_default()

                    draw.text((110, 90), label.upper(), fill=accent, font=fB)

                    words = text.split()
                    lines, cur = [], []
                    for w in words:
                        cur.append(w)
                        if len(" ".join(cur)) > 52:
                            lines.append(" ".join(cur[:-1]))
                            cur = [w]
                    lines.append(" ".join(cur))

                    y = 140
                    for line in lines[:6]:
                        draw.text((110, y), line, fill=fg, font=fM)
                        y += 44

                    draw.text((W - 230, H - 50), f"IELTS Band {target_score}", fill=muted, font=fS)
                    return np.array(img)

                q_frame = make_frame(video_style, "Question", question)
                a_frame = make_frame(video_style, "Answer", english_script)
                progress.progress(70)

                # ── 영상 합성 ─────────────────────────────────────────────────
                status.text("🎞️ 영상 합성 중...")
                q_audio = AudioFileClip(q_audio_path)
                a_audio = AudioFileClip(a_audio_path)
                q_clip = ImageClip(q_frame).set_duration(q_audio.duration + 1.5).set_audio(q_audio)
                a_clip = ImageClip(a_frame).set_duration(a_audio.duration + 2.0).set_audio(a_audio)
                final = concatenate_videoclips([q_clip, a_clip], method="compose")

                output_path = os.path.join(tmpdir, "ielts_speaking.mp4")
                status.text("💾 저장 중...")
                progress.progress(85)
                final.write_videofile(
                    output_path, fps=24, codec="libx264",
                    audio_codec="aac", logger=None, threads=2
                )
                progress.progress(100)
                status.empty()

                with open(output_path, "rb") as f:
                    video_bytes = f.read()

                st.success("🎉 영상 완성!")
                st.download_button(
                    "⬇️ MP4 다운로드",
                    data=video_bytes,
                    file_name="ielts_speaking.mp4",
                    mime="video/mp4",
                    use_container_width=True
                )
                st.info("📤 YouTube Studio → 동영상 만들기 → 업로드")

                q_audio.close()
                a_audio.close()
                final.close()

            except Exception as e:
                st.error(f"오류: {e}")
                import traceback
                st.code(traceback.format_exc())

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.caption("AI: Gemini 2.0 Flash (무료 · 하루 1,500회) · TTS: gTTS / Chatterbox (무료) · 영상: MoviePy")

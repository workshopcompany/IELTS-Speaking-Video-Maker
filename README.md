# 🎙️ IELTS Speaking Video Maker

한글로 답변 → IELTS 영어 스크립트 자동 생성 → 내 목소리 MP4 영상 제작

[▶ 앱 바로 가기](https://workshopcompany-ielts-speaking-video-maker.streamlit.app)

---

## 주요 기능

- IELTS Part 1 / 2 / 3 질문 랜덤 제공
- 한글로 내 스토리를 쓰면 Band 5.0~8.0 수준에 맞는 영어 답변 자동 생성 (Gemini 2.0 Flash)
- 생성된 스크립트를 음성으로 변환 → MP4 영상 다운로드
- 목소리 선택: 기본 TTS (gTTS) 또는 내 목소리 클로닝 (Chatterbox, 10초 녹음)

---

## 로컬 실행

```bash
git clone https://github.com/workshopcompany/IELTS-Speaking-Video-Maker
cd IELTS-Speaking-Video-Maker
pip install -r requirements.txt
streamlit run app.py
```

---

## Streamlit Cloud 배포 후 Secrets 설정

Streamlit Cloud → 앱 설정 → Secrets 탭에 아래 내용 추가:

```
GEMINI_API_KEY = "여기에_무료_키_입력"
```

무료 키 발급: [aistudio.google.com/apikey](https://aistudio.google.com/apikey) (카드 불필요)

---

## 내 목소리 클로닝 (선택)

```bash
pip install chatterbox-tts
```

앱 실행 후 Step 4 → 🟢 탭 → 10초 이상 녹음 파일 업로드

---

## 기술 스택

| 역할 | 도구 | 비용 |
|------|------|------|
| 영어 스크립트 생성 | Gemini 2.0 Flash | 무료 (1,500회/일) |
| 기본 음성 합성 | gTTS | 무료 |
| 내 목소리 클로닝 | Chatterbox TTS | 무료 (MIT) |
| 영상 합성 | MoviePy | 무료 |
| 앱 배포 | Streamlit Cloud | 무료 |

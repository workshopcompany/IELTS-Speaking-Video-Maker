# 🎙️ IELTS Speaking Video Maker

한글로 답변 → IELTS 영어 스크립트 자동 생성 → 내 목소리 MP4 영상 제작

[▶ 웹 앱 바로 가기](https://workshopcompany-ielts-speaking-video-maker.streamlit.app) &nbsp;|&nbsp; [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/workshopcompany/IELTS-Speaking-Video-Maker/blob/main/IELTS_Colab.ipynb)

---

## 사용 방법 — 두 가지 모드

| | 웹 앱 (Streamlit) | Colab 노트북 |
|---|---|---|
| 접근 방법 | URL 접속 | Google Colab 실행 |
| AI 스크립트 | ✅ Gemini 2.0 Flash | ✅ Gemini 2.0 Flash |
| 목소리 | 기본 TTS (gTTS) | ✅ **내 목소리 (OpenVoice)** |
| GPU 필요 | ❌ | ✅ T4 무료 제공 |
| 추천 용도 | 빠르게 연습할 때 | 유튜브 업로드용 영상 만들 때 |

---

## ① 웹 앱 사용법

1. [▶ 앱 바로 가기](https://workshopcompany-ielts-speaking-video-maker.streamlit.app) 클릭
2. IELTS 질문 선택 (랜덤 or 직접 입력)
3. 한글로 내 스토리 답변 입력
4. AI가 목표 Band 수준의 영어 스크립트 생성
5. MP4 영상 다운로드

---

## ② Colab 내 목소리 버전 사용법

1. 위 **Open in Colab** 배지 클릭
2. 런타임 → 런타임 유형 변경 → **T4 GPU** 선택
3. 셀 순서대로 실행
   - 셀 1~2: 패키지 및 모델 설치 (최초 1회만, 약 10분)
   - 셀 3: Gemini API Key 입력
   - 셀 4: 내 목소리 녹음 파일 업로드 (10초 이상 MP3/WAV)
   - 셀 5: 모델 로드 (최초 1회만)
   - 셀 6: 질문·답변 입력 후 실행 → MP4 자동 다운로드

> 셀 6의 `QUESTION`과 `KOREAN_ANSWER`만 바꿔서 반복 실행하면 됩니다.

**녹음 팁:** ChatGPT에게 "10초 분량의 자연스러운 영어 문장 만들어줘"라고 부탁한 뒤, 조용한 방에서 스마트폰으로 또박또박 녹음하세요.

---

## 로컬 직접 실행 (웹 앱 버전)

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

무료 키 발급: [aistudio.google.com/apikey](https://aistudio.google.com/apikey) (카드 불필요, 하루 1,500회 무료)

---

## 기술 스택

| 역할 | 도구 | 비용 |
|------|------|------|
| 영어 스크립트 생성 | Gemini 2.0 Flash | 무료 (1,500회/일) |
| 기본 음성 합성 | gTTS | 무료 |
| 내 목소리 클로닝 | OpenVoice V2 (MIT) | 무료 |
| 영상 합성 | MoviePy | 무료 |
| 웹 앱 배포 | Streamlit Cloud | 무료 |
| GPU 환경 | Google Colab T4 | 무료 |

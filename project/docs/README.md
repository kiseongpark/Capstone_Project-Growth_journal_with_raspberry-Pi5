## Gemini API, gTTS, Pushbullet API 사용환경 세팅


### 1. Gemini API
---


1. **Google Generative AI SDK**


```bash
pip install "google-generativeai>=0.7,<1"

```

2. **Google API Key 안전하게 설정**

절대 코드에 키를 하드코딩하지 말고 환경변수로 씁니다.

```bash
# 셸에만 임시 등록(현재 터미널 세션 동안만)
export GOOGLE_API_KEY="여기에_발급받은_키"

# 영구 등록(다음 로그인부터 자동 반영)
echo 'export GOOGLE_API_KEY="여기에_발급받은_키"' >> ~/.bashrc
source ~/.bashrc

```

코드에선 이렇게 사용:

```python
import os, google.generativeai as genai
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

```

### 2. gtts
---

```bash
pip install gTTS
sudo apt-get update && sudo apt-get install -y mpg123

```

코드에선 이렇게 사용:

```python
import re
import subprocess
from pathlib import Path
from gtts import gTTS

```


### 3. Pushbullet API
---

   ```python
pip install pushbullet.py
export PUSHBULLET_API_KEY="pushbullet API key"

```

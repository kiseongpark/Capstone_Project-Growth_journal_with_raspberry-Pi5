## 성장일지 시스템 구현 in Raspberry Pi

라즈베리파이에 연결된 카메라로 식물을 인식하고, Gemini API를 사용하여 성장일지를 작성하고, 그것을 사용자에게 Pushbullet API를 활용하여 전달하는 시스템을 구현. 
우리 제품은 독거노인을 대상을 제작하였기 때문에 성장일지를 요약한 내용을 TTS로 출력하여, 사용자가 그것을 들을 수 있도록 기능을 구현하였다.


### 라즈베리파이 환경 세팅(Raspberry Pi 5)

#### 1. 가상환경 및 각종 패키지 설치
---

1. **가상환경 세팅**

```bash
python3 -m venv --system-site-packages project
```

python을 활용해서 가상환경을 만들어준다. 가상환경 이름은 project로 정하였다.

```python
source project/bin/activate
```

가상 환경을 실행시키는 코드이다.


2. **핵심 과학 스택 + OpenCV(headless)** 

```bash
pip install "numpy>=2.0,<2.3" opencv-python-headless==4.12.0.88

```

3. **Ultralytics + PyTorch (CPU)**
    
라즈베리파이에선 CPU 빌드가 가장 수월합니다.
    

```bash
sudo apt update
sudo apt install python3-pip -y
pip install -U pip
# PyTorch(CPU) - 공식 인덱스에서 설치 시 ARM64도 지원되는 경우가 많습니다.
pip install --extra-index-url https://download.pytorch.org/whl/cpu torch torchvision torchaudio

# Ultralytics 본체
pip install "ultralytics>=8.3,<9"

```

##### 2. 파일 구조 및 실행법
---

project 폴더 안 파일은 아래 사진과 같이 구성된다.


<img width="500" height="400" alt="image (17)" src="https://github.com/user-attachments/assets/d1c1b384-93e8-42f2-bf4a-539ed92aae85" />


1. **편집기로 새 파일 생성(직접 위치가서 생성해도됨) - 자유롭게**
    
 ```bash
 nano run.py
    
  ```
    
2. **같은 폴더에 best1.pt 넣기 (사전에 학습한 모델)**
3. **가상환경 활성화 후 실행**

```bash
source project/bin/activate
cd project
python run.py

```

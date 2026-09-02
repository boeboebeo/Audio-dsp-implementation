"""

git add .
git commit -m "feat : BPF 1, 2 comparison"
git push origin main

wip : work in progress. 아직 작업중(미완인 프로젝트 올릴때 쓰는 커밋 컨벤션(관습))

-commit type-d
feat:     새로운 기능 추가
fix:      버그 수정
docs:     문서/주석 수정 (코드 동작 변경 없음)
style:    코드 포맷팅, 세미콜론 등 (로직 변경 없음)
refactor: 코드 리팩토링 (기능 변경 없음)
test:     테스트 코드 추가/수정
chore:    빌드, 설정 파일 수정



**기본 구조**
def main():
    # 전체 순서만 조립

SAMPLE_RATE = 48000


#입력신호 생성
def create_sine(SAMPLE_RATE):


def create_white_noise():


def create_impulse():



#Delay 적용하기
def apply_delay():

def ms_to_samples():

def db_to_linear():

def save_wav():

def plot_waveform():

def plot_spectrum():


**단축키**
cmd + option + f : 글자 다 바꾸기


"""
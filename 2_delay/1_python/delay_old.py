""" [DELAY]

1) 입력신호 생성
2) delay 적용 (delay time, mix, feedback <= 파라미터 세 종류)
    : 새로운 출력 배열을 만들고, delay 위치에 입력 샘플을 원하는 위치에 복사하는 원리
    : y[n] = x[n - D] <- 현재 출력 샘플은 D 만큼 과거의 입력샘플을 가져온다.

    //여기서는 구현 안되지만 juce 에서는 실시간 조절이기때문에 Circular Buffer를 사용하게 됨

    1. Delay time
    x[n] (input)                         
    index:
    0  1  2  3  4  5  6
    1  2  3  4  5  6  7

    => Delay = 3samples 라면 

    y[n] (output)
    index:
    0  1  2  3  4  5  6
    0  0  0  1  2  3  4     //지연된 위치에 input 배열 복사함

    2. Feedback 
    : y[n] = x[n] + ay[n-D]

    3. Mix
    : y[n] = x[n](dry) + x[n-D](wet)

3) dB, time 제어
4) save wav file
5) plot

"""

import numpy as np
import matplotlib.pyplot as plt


def main():
    # 전체 순서 조립

    sample_rate = 48000
    freq = 1000 #Hz
    duration = 1.0 #s

    delay_ms = 100
    wet = 0.5  # 0 ~ 1.0 까지의 범위 (%)
    feedback = 0.5 # 0 ~ 1.0까지의 범위 (%)

    num_samples = int(sample_rate*duration) 

    t = np.linspace(0, duration, num_samples, endpoint=False)

    create_sine(freq, t) #여기서 넣어주는 값은 실제 값
    create_white_noise(num_samples)
    create_impulse(num_samples)

    delay_samples = ms_to_samples(
        delay_ms,
        sample_rate
    )


#입력신호 생성
def create_sine(freq, t): #여기서 받는 매개변수는 그 값을 받을 이름
    sine = np.sin(2*np.pi*freq*t)

    return sine


def create_white_noise(num_samples):
    noise = np.random.uniform(-1, 1, num_samples)   #len()은 리스트, 배열처럼 길이가 있는 객체에 쓰이는 함수. 여기서는 바로 num_samples 넣어도됨

    return noise


def create_impulse(num_samples):
    impulse = np.zeros(num_samples)
    impulse[0] = 1.0 #DSP 신호는 보통 float amplitude(-1.0 ~ 1.0)사용 -> 1.0으로 표현

    return impulse



#Delay 적용하기
#Feedback 없는 버전
def apply_delay(input_signal, delay_samples, wet):
    #먼저 비어있는 출력배열 만들기
    delayed = np.zeros(len(input_signal))
    delayed[delay_samples:] = input_signal[:-delay_samples]
        #출력배열의 delay_samples 이후 위치에, 입력신호의 마지막 delay_samples 개를 제외한 앞부분을 넣음
        #array[:-3] : 음수면 -> 끝에서 3개를 제외하고 전부
        #끝에서 N번째 위치까지 . 입력의 마지막 N 를 잘라내어야 길이가 맞음

    output = input_signal * (1-wet) + delayed * wet

    return output

#Feedback 있는 버전
def apply_delay_with_feedback(input_signal, delay_samples, wet, feedback):
    
    delayed = np.zeros(len(input_signal))

    for i in range(delay_samples, len(input_signal)):
        output[i] = input_signal[i] + 

    return output



#실제 사용자가 조절하는 값은 Time -> samples 로 변환
#(사람이 조절하는 물리단위 -> DSP 가 계산하는 내부 단위로 변환하는 단계가 항상 존재함)
def ms_to_samples(delay_ms, sample_rate):
    delay_samples = int((delay_ms / 1000) * sample_rate)

    return delay_samples


# Output level 조절할때 말고는 안쓰임
# def db_to_linear():
    


def save_wav():

def plot_waveform():

def plot_spectrum():
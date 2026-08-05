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
    : y[n] = x[n] + g*y[n-D]
        // g = feedback (0 ~ 1.0) 사이의 값
        // n 번째 출력은 앞 샘플들의 딜레이신호에 영향을 받음

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
    mix = 0.5  # 0 ~ 1.0 까지의 범위 (%)
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
def apply_delay(input_signal, delay_samples, mix):
    #먼저 비어있는 출력배열 만들기
    delayed = np.zeros(len(input_signal))
    delayed[delay_samples:] = input_signal[:-delay_samples]
        #출력배열의 delay_samples 이후 위치에, 입력신호의 마지막 delay_samples 개를 제외한 앞부분을 넣음
        #array[:-3] : 음수면 -> 끝에서 3개를 제외하고 전부
        #끝에서 N번째 위치까지 . 입력의 마지막 N 를 잘라내어야 길이가 맞음

    output = input_signal * (1-mix) + delayed * mix
        #전체(dry + wet)합해서 1이 되도록 출력

    return output


#Feedback 있는 버전
def apply_delay_with_feedback(input_signal, delay_samples, mix, feedback):
    
    #출력
    output = np.zeros(len(input_signal))

    #Delay buffer
    delay_buffer = np.zeros(len(input_signal) + delay_samples)
        #delay_samples 만큼의 index 더 늘린 공간
    

    # 2. Delay + Feedback 계산
    for i in range(len(input_signal)):

        #현재 입력
        dry_signal = input_signal[i]

        #Delay buffer 에서 읽기
        delayed = delay_buffer[i] 
            #과거에 delay_buffer[i]에 저장해둔 값이 지금 영향을 받게 함

        #Mix
        output[i] = dry_signal * (1-mix) + delayed * mix

        #Feedback 을 적용해서 미래 위치에 저장
        #delay buffer 는 Feedback loop 내부의 상태 (state) <- 다음 반복을 위한 에너지를 저장하는 곳
        delay_buffer[i+delay_samples] += dry_signal + delayed * feedback
            #그냥 =을 쓰면 기존에 그 위치에 저장되어 있던 값이 덮어써져 버림
            #실제 Delay 에서는 원래 들어있던 echo + 새롭게 생성된 echo가 합쳐져야 함

    return output

""" 1) example. input_signal = [1 0 0 0 1 0 0 0 ...]

i = 0 
: output [0.5 0 0 0 0 0 0 0 ]
: delay_buffer [0 0 0 1 0 0 0 0 0 ..] <- 여기 idx3의 값이 i=3 일때 영향

i = 1
: output [0.5 0 0 0 0 0 0 0 0 ]
: delay_buffer [ 0 0 0 1 0 0 0 0 0 ] 

i = 3
: output [0.5 0 0 0.5 0 0 0 0 0 ]
: delay_buffer [0 0 0 1 0 0 0.5 0 0 0 ]  <-idx6 의 값이 0.5 : 뒤에서 또 feedback이랑 곱해져서 또 작아짐

i = 4
: output [0.5 0 0 0.5 0.5 0 0 0 0]
: delay_buffer [0 0 0 1 0 0 0.5 1 0 ...]

i = 6
: output [0.5 0 0 0.5 0.5 0 0.25 0 0..]
: delay_buffer [0 0 0 1 0 0 0.5 1 0 0.25..] 

=> 미래의 인덱스에 저장해둔 값이, 시간이 지나 현재위치가 되었을때 출력에 사용됨
ex. i = 0
        -> delay buffer[3]에 저장
    i = 4
        -> delay buffer[7]에 저장해서 i = 7일때 사용됨

"""

"""2) example. input_signal = [1 0 0 1 0 0 0 0...]

i = 0
: output [0.5 0 0 0 0 0 0 0]
: delay_buffer [0 0 0 1 0 0 0 ]

i = 3 
: output [0.5 0 0 1 0 0 0 0]
: delay_buffer [0 0 0 1 0 0 1.5 0 0.. ]
"""
            
        
"""
    delayed[i] = input_signal[i-delay_samples]

    example. delay_sample = 3일때

    0 1 2 3 4 5 6 (index)
    1 0 0 0 0 0 0 (input_signal)
    ...
    0 0 0 1 0 0 0 (output_signal) <- index 3일때 input[0]이 output[3]으로 옴

    i=0) delayed[0] = input_signal[0-3] = 0
    i=3) delayed[3] = input_signal[3-3] = 1 

    """

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
    return 


""" CHANGE LOG

1) 260805
    : 실시간 구현에서는 현재 버퍼위치에 저장하고, 시간이 흘러 readpoint 가 그 위치 도달하면 읽는다
    => readIndex, writeIndex 가 따로 존재함
    : 현재 python 에서는 미래의 index 에 딜레이되는 사운드를 저장해두고서 
        시간이 지나 해당 index (i + delay_samples)가 되었을때 영향을 받게 함


    """
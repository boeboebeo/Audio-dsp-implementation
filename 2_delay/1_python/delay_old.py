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
import soundfile as sf
import os



def main():
    # 전체 순서 조립

    sample_rate = 48000
    freq = 1000 #Hz
    duration = 1.0 #s

    # delay_ms = 100 #밑에서 한번에 처리할 예정
    mix = 0.5  # 0 ~ 1.0 까지의 범위 (%)
    # feedback = 0.2 # 0 ~ 1.0까지의 범위 (%)

    num_samples = int(sample_rate*duration) 

    t = np.linspace(0, duration, num_samples, endpoint=False)

    #input_signal 생성
    input_sine = create_sine(freq, t) #여기서 넣어주는 값은 실제 값
    input_noise = create_white_noise(num_samples)
    input_impulse = create_impulse(num_samples)

    #한번에 처리
    signals = [
        ("sine", input_sine),
        ("noise", input_noise),
        ("impulse", input_impulse)
    ]

    delay_times = [50, 100, 300]
    feedbacks = [0.3, 0.6, 0.9]

    results = {
        "impulse": [],
        "sine" : [],
        "noise" : []
    } #빈 배열 하나 만들어서 그 내용 다 모을 예정

    for signal_name, signal in signals:
        for delay_ms in delay_times:
            for feedback in feedbacks:

                #delay time circulation
                delay_samples = ms_to_samples(
                    delay_ms,
                    sample_rate
                )

                #delay apply
                output_signal = apply_delay_with_feedback(
                    signal,
                    delay_samples,
                    mix,
                    feedback
                )

                #save wav
                save_wav(
                    signal_name, delay_ms, feedback, output_signal, sample_rate
                )

                #result 모아두기 -> plot 하려고!
                results[signal_name].append({
                    "delay_ms" : delay_ms,
                    "feedback" : feedback,
                    "output" : output_signal # '=' 아니고 ':' 이여야 함!
                })

    #plot 
    plot_delay(results, sample_rate)




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
    #ouput length 가 짧으면 딜레이로 인해서 생기는 늘어난 시간은 나오지 않게됨 
    output_length = len(input_signal) + delay_samples*10
    output = np.zeros(output_length)

        #input_signal 은 len() 필요
        #output_length 는 이미 int 라서 len() 없어야 함 (이미 길이 숫자)

    #Delay buffer
    delay_buffer = np.zeros(len(input_signal) + delay_samples*10)
        #delay_samples 만큼의 index 더 늘린 공간
    

    # 2. Delay + Feedback 계산
    for i in range(output_length):
        #이렇게 계산해줘야( range(output_length) ) <- input_signal 길이를 넘어가도 계산이 됨 (feedback 부분)


        #현재 입력 (입력이 아직 존재한다면)
        if i < len(input_signal):
            dry_signal = input_signal[i]
        
        else:
            dry_signal = 0.0


        #Delay buffer 에서 읽기
        delayed = delay_buffer[i] 
            #과거에 delay_buffer[i]에 저장해둔 값이 지금 영향을 받게 함

        #Mix
        output[i] = dry_signal * (1-mix) + delayed * mix
        

        #Feedback 을 적용해서 미래 위치에 저장
        #delay buffer 는 Feedback loop 내부의 상태 (state) <- 다음 반복을 위한 에너지를 저장하는 곳
        if i + delay_samples < output_length:
            delay_buffer[i+delay_samples] = dry_signal + delayed * feedback
            

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
            


#실제 사용자가 조절하는 값은 Time -> samples 로 변환
#(사람이 조절하는 물리단위 -> DSP 가 계산하는 내부 단위로 변환하는 단계가 항상 존재함)
def ms_to_samples(delay_ms, sample_rate):
    delay_samples = int((delay_ms / 1000) * sample_rate)

    delay_samples = max(1, delay_samples)
        # 만약 0 sample 딜레이 일 경우, 현재 인덱스 자리에 지연음이 자리잡아 버림
        # 따라서 최소 1 sample 을 보장하게 만듦
        # 사용자가 0ms 를 선택해도 실제로는 1 sample delay 가 생기지만 
        # 거의 20.8 micro second 여서 매우 짧음

    return delay_samples

    


def save_wav(signal_name, delay_ms, feedback, output, sample_rate):

    output_dir = "2_delay/1_python/testwav"

    os.makedirs(output_dir, exist_ok=True)

    #file name (wav 저장할때 쓸 용도)
    file_name = (
        f"{signal_name}"
        f"_delay{delay_ms}ms"
        f"_fb{int(feedback*100)}%.wav"
    )   # file name 은 하나로 이어진거지 튜플이 아니기 때문에 ',' 쉼표 없애기

    filepath = os.path.join(output_dir, file_name)


    sf.write(filepath,
             output, sample_rate, subtype = "FLOAT") 
            #subtype="FLOAT" : 32-bit floating point wav 로 저장한다는 뜻 
            #int16 사용할 경우, 32767 이상이면 바로 잘려버림
            #위에서 filepath = .. 에서 이미 file_name 넘겼기 때문에 또 넘기면 안됨


def plot_delay(results, sample_rate):

    fig, axes = plt.subplots(2, 3, figsize=(12, 8))

    for signal_name in ["impulse", "sine"]:

        signal_results = results[signal_name]
        axes = axes.flatten()

        for ax, result in zip(axes, signal_results):

            output = result["output"]
            delay_ms = result["delay_ms"]
            feedback = result["feedback"]

            time = np.arange(len(output)) / sample_rate
            
            ax.plot(time, output)

            ax.set_title(
                f"Delay {delay_ms}ms / Feedback : {feedback}"
            )


    plt.tight_layout()
    plt.show()


    





if __name__ == "__main__":
    main()
    #이게 함수 위에 있었더니 애초에 그 밑에 있는 함수들을 인지못함 
    #python 은 위 -> 아래로 읽어나가기 때문에 이 표시는 함수 맨 아래에 두기
    #직접 실행할때만 사용되는 코드 (다른 프로젝트에서 main() 실행안하고 함수만 가져다가 쓸때!)






# def plot_spectrum():
#     return 





""" CHANGE LOG

1) 260805
    : 실시간 구현에서는 현재 버퍼위치에 저장하고, 시간이 흘러 readpoint 가 그 위치 도달하면 읽는다
    => readIndex, writeIndex 가 따로 존재함
    : 현재 python 에서는 미래의 index 에 딜레이되는 사운드를 저장해두고서 
        시간이 지나 해당 index (i + delay_samples)가 되었을때 영향을 받게 함

    : if __name__ = "__main__":
        main() 위치 조정

        
2) 260806 
    + output tail 은 어떻게 처리하면 좋을지?
    + feedback 이 1이상의 값이 되어버리면 점점 소리가 증폭
        => 이걸 어떻게 해결?
        feedback = np.clip(feedback, 0, 0.99)    ?

    + 만약 delay_samples = 0 이라면 
    delay_buffer[i+delay_samples] = dry_signal + delayed * feedback
    
    : 위 코드에서 바로 원본 타이밍 자리에 셋팅이 되어버린다. 
    => if delay_samples < 1 일때 어떻게 해야할지 따로 처리해줘야함

    + sine, noise, impulse 한번에 처리하는 방법


3) 260807
    +for i in range(len(input_signal)):
    : 때문에 입력길이만큼만 output 을 계산하고 있음
    => 근데 delay_buffer 에는 이미 입력이 끝난뒤에 재생될 feedback 들도 저장되어 있음

    +plot 구성하기


    """
""" [GAIN]

1) 우선 파형을 만들고 (sine, noise)
    - Digital audio 는 +/- 1.0을 기준으로 사용함
    - 16bit PCM 이라면 저장되는 값은 메모리에서 float32 계산 -> -32768 ~ +32768 범위 (실제파일안에는 정수(int)가 저장됨)
    - 그 큰 수를 매번 계산하려면 불편 -> 1.0 으로 정규화(normalize)해서 16-float 으로 바꿔줌
    -> 따라서 0dBFS(16Bit 에서의 32767) 이상의 값이 나오면 그냥 32767로 잘라버림

    **근데 32-bit float 는 정수가 아니라 IEEE Floating point 를 사용함
    => 이건 정수가 아니라서 1.0을 넘어가는 실수 계산가능하다. 
    => 따라서 0dBFS 를 넘어가는 값도 메모리 안에서는 존재가능
    
2) 레벨 조정
    => dB 단위로 조절할 수 있도록 dB 로 변환
    **근데 실무 관례상 순서가 반대다. 사용자가 dB로 입력을 하면 linear 로 변환해서 실제 신호에 곱함
     (실무 순서에서는)
    - dB 가 primary parameter

3) wav.file 출력

4) FFT 비교

=> 전체적으로 코드 정확성, reusability, edge case(gain=0, gain<0 같은 경계값)
    을 더 유의하면서 정리해봐야 할듯! 
    **정상 케이스 (Gain>0) 만 염두에 두고 짜여진 느낌이면 경계값 처리 누락이 에러가 뜰 수 있음
      (실무에서의 오디오 DSP 버그 상당수가 0, 음수, 무한대 에서 나오게 됨)

"""

import numpy as np
import matplotlib.pyplot as plt
import math
import soundfile as sf
    # wav 저장을 위한 라이브러리
    # or from pathlib import Path 해서 폴더가 없어도 자동으로 만들어 주게끔 하는 라이브러리도 굳


# 1) sine 제작 
def create_sine():
    fs = 48000
    freq = 200
    duration = 1.0

    t = np.linspace(0, duration, int(duration*fs), endpoint=False)

    sine_wave = np.sin(2*np.pi*freq*t)

    return t, sine_wave

# 2) white noise 제작
def create_noise():
    fs = 48000
    duration = 1.0

    t = np.linspace(0, duration, int(duration*fs), endpoint=False)

    white_noise = np.random.uniform(-1.0, 1.0, len(t))
        # 범위: -1.0 ~ +1.0 의 랜덤한 값을 가지는 신호가 만들어짐

    """noise 만드는 여러가지 방법

    1) np.random.uniform(-1, 1, N)

    2) np.random.normal(0.0, 0.2, num_samples)
        - 평균: 0
        - 표준편차 : 0.2 인 노이즈 생성됨

    3) np.random.randn(N)
    """
    
    return t, white_noise

def apply_gain():
    t, sine_wave = create_sine()
    t, white_noise = create_noise()


    # gain 을 조절하려면 곱하기를 해야함 
    # +, - 를 한다면 진폭이 0 에서 -> -값으로 갈수도 있는데, 그러면 레벨이 더 커지는 것
    # dB 로 조절
    gain = [1, 0, 0.5, -0.5, -2, 2]
        # 이 값은 dB 로 변환하기 전의 linear gain : 신호에 그대로 곱하는 값 
        # 아 근데 -값을 곱하면 위상이 뒤집힘! + 게인 조절 
        # 그래서 -값의 게인을 곱하면 위상이 뒤집히며 -> dB 계산시 'nan' 이라고 뜨게 됨
        # 차라리 음수 게인을 쓰지 말고, Phase invert 기능을 따로 쓰는게 나음
            # 위상은 별도로 관리!
        # 0을 곱하게 되면 dB 로는 -inf (-무한대)

    """
    | Linear Gain | dB        | 의미      |
    | ----------- | --------- | ------   |
    | 2.0         | +6.02 dB  | 두 배 커짐 |
    | 1.0         | 0 dB      | 변화 없음  |
    | 0.5         | -6.02 dB  | 절반      |
    | 0.25        | -12.04 dB | 1/4      |
    | 0.0         | -∞ dB     | 완전 무음  |

    """

        # gain_linear 구하는 법 
    """ 
    example1. 6dB는 linear_gain 으로는 몇?
        20*np.log10(linear_gain) = 6dB <= 두배 한것이므로
        np.log10(linear_gain) = 6/20

        10**(3/10) = linear_gain = 약 1.995 => 거의 2 가 나오게 된다.

    example2. -6dB는 linear_gain 으로 몇?
        20*np.log10(linear_gain) = -6
        np.log10(linear_gain) = -3/10

        10**(-3/10) = linear_gain = 0.501... => 거의 0.5배

    **실제 DSP 에서는 사용자가 dB를 조정하고 내부 DSP 는 
      항상 Linear gain 으로 변환해서 곱셈을 수행함        
        """

    n = len(gain)

    # subplots 의 가로 세로 개수가 내가 gain 에 수를 더 추가해도 자동으로 조정되게끔 하게끔
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)
        # 이렇게 행과 열을 정함
        # gain 개수 1개 : rows 1, cols 1
        # gain 개수 3개 : rows 2, cols 2
        # gain 개수 6개 : rosw 2, cols 3
        # 그 후에 plt.subplots() 가 반환하는 axes 를 1차원으로 flatten(펼쳐)버리면 됨
        # axes = axes.flatten()
        # 이렇게 하면 최대한 정사각형에 가깝게 배치됨! 


    # 1) sine_wave - gain process
    fig, axes = plt.subplots(rows, cols, figsize=(12, 8))
        #이게 for 문 밖에 있어야 도화지 하나만 그림
        #밑 for 문 내부에 넣었더니 그 gain 개수만큼 도화지가 그러졌었다.

    axes = axes.flatten()

    for index, level in enumerate(gain):

        apply_gain = sine_wave * level
            # 이건 근데 함수 이름과 변수 이름을 다르게 가지는게 좋을듯 차라리 -> "output"
        dB = 20*np.log10(np.abs(level))
            # 사실상 여기서 np.abs를 처리해놓았기 때문에 음수 linear_gain 들도 동일하게 변조가 됨

        # wav file 저장
        sf.write(f"1) gain/output/{dB:.3f} dB_sine_gain.wav", apply_gain, 48000, subtype='FLOAT')
            # PCM audio 에서는 -1 ~ +1까지만 레벨이 조절될 수 있기때문에 
            # 매우 많이 넘어가게 되면 바로 클리핑 
            # , 48000, subtype='FLOAT' : 처리로, 헤드룸을 보존하면서 나중에 FFT 분석하도록 함 

        # original_wave - visualization
        # original signal
        if index == 0:
            ax = axes[index]
            ax.plot(t, sine_wave, linewidth=1.5, color='green')
            ax.set_title('Original_sinewave')
            ax.set_ylabel('Amplitude')
            ax.set_xlabel('time')
            ax.set_ylim(-3, 3)
            ax.grid(True, alpha=0.3)

        # gain up
        elif level >= 0:
            ax = axes[index]
            ax.plot(t, apply_gain, linewidth=1.5, color='blue')
            ax.set_title(f'gain : {dB:.3f} dB\n(level:{level})')
            ax.set_ylabel('Amplitude')
            ax.set_xlabel('Time')
            ax.set_ylim(-3, 3)
            ax.grid(True, alpha=0.3)

        # gain down
        else:
            ax = axes[index]
            ax.plot(t, apply_gain, linewidth=1.5, color='red')
            ax.set_title(f'gain : {dB:.3f} dB\n(level:{level})')
            ax.set_ylabel('Amplitude')
            ax.set_xlabel('Time')
            ax.set_ylim(-3, 3)
            ax.grid(True, alpha=0.3)


    plt.tight_layout()
    plt.show()


    # 2) white-noise_gain process 
    fig, axes = plt.subplots(rows, cols, figsize=(12, 8))

    axes = axes.flatten()

    for index, level in enumerate(gain):

        apply_gain = white_noise * level
        dB = 20*np.log10(np.abs(level))

        # wav file 저장
        sf.write(f"1) gain/output/{dB:.3f} dB_noise_gain.wav", apply_gain, 48000, 48000, subtype='FLOAT')
            # PCM audio 에서는 -1 ~ +1까지만 레벨이 조절될 수 있기때문에 
            # 매우 많이 넘어가게 되면 바로 클리핑 

        # original_wave - visualization
        # original signal
        if index == 0:
            ax = axes[index]
            ax.plot(t, white_noise, linewidth=1.5, color='green')
            ax.set_title('Original_noisewave')
            ax.set_ylabel('Amplitude')
            ax.set_xlabel('time')
            ax.set_ylim(-3, 3)
                # 근데 이렇게 할지 게인이 높아지면 표현이 안되므로
                # ylim = max(abs(g) for g in gain) * 1.2 -> 이런식의 동작이 더 안전
            ax.grid(True, alpha=0.3)

        # gain up
        elif level >= 0:
            ax = axes[index]
            ax.plot(t, apply_gain, linewidth=1.5, color='blue')
            ax.set_title(f'gain : {dB:.3f} dB\n(level:{level})')
            ax.set_ylabel('Amplitude')
            ax.set_xlabel('Time')
            ax.set_ylim(-3, 3)
            ax.grid(True, alpha=0.3)

        # gain down
        else:
            ax = axes[index]
            ax.plot(t, apply_gain, linewidth=1.5, color='red')
            ax.set_title(f'gain : {dB:.3f} dB\n(level:{level})')
            ax.set_ylabel('Amplitude')
            ax.set_xlabel('Time')
            ax.set_ylim(-3, 3)
            ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()



apply_gain()


"""CHANGE LOG

1) 260720 
: gain 기본 틀 구성, axes 에 배열 개수에 맞춰서 넣는거 한번 다시 살펴보기(특히 flatten)
: 그리고 지금 dB , level 이 뭔가 혼란스럽게 출력이 나오는데
    - 레벨이 -값이면 안되는건지?
    - 그리고 여기의 이 값이 dB 로 표기를 하는게 맞긴 한건지
    - 그리고 실제 DSP 에서는 이 최대한계 리미팅을 어떻게 하는지.. 체크

2) 260721
 : gain up/down 에 따라서 색상 다르게 함
 : wav file 추출함
 : gpt + claude 피드백 받고 주석 및 코드 수정
 : Feedback 내용
    - apply_gain() 에 너무 많은 내용이 들어가있음
        => process_gain(), plot_signal(), save_wav(), plot_fft()이렇게 각자 만들기
           (재사용성 - Reusability 키우기)
    - 추가했으면 하는 내용 : Peak, RMS, FFT, Clipping detection

"""


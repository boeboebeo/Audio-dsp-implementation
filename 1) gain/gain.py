""" [GAIN]

1) 우선 파형을 만들고 (sine, noise)
2) 그 레벨을 줄임
    => dB 단위로 줄일수있게 해야함
3) 출력된 사운드에는 레벨이 줄어들어 있음
4) FFT 비교

"""

import numpy as np
import matplotlib.pyplot as plt
import math


# 1) sine 제작 
def create_sine():
    fs = 48000
    freq = 20
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

    fig, axes = plt.subplots(rows, cols, figsize=(12, 8))
        #이게 for 문 밖에 있어야 도화지 하나만 그림
        #밑 for 문 내부에 넣었더니 그 gain 개수만큼 도화지가 그러졌었다.

    axes = axes.flatten()

    for index, level in enumerate(gain):

        apply_gain = sine_wave * level
        dB = 20*np.log10(level)

        # original_wave - visualization
        if index == 0:
            ax = axes[index]
            ax.plot(t, sine_wave, linewidth=1.5, color='green')
            ax.set_title('Original_sinewave')
            ax.set_ylabel('Amplitude')
            ax.set_xlabel('time')
            ax.set_ylim(-3, 3)
            ax.grid(True, alpha=0.3)

        ax = axes[index]
        ax.plot(t, apply_gain, linewidth=1.5, color='red')
        ax.set_title(f'gain : {dB}')
        ax.set_ylabel('Amplitude')
        ax.set_xlabel('Time')
        ax.set_ylim(-3, 3)
        ax.grid(True, alpha=0.3)


    plt.tight_layout()
    plt.show()


apply_gain()

"""Record

1) 0720 
: gain 기본 틀 구성, axes 에 배열 개수에 맞춰서 넣는거 한번 다시 살펴보기(특히 flatten)
: 그리고 지금 dB , level 이 뭔가 혼란스럽게 출력이 나오는데
    - 레벨이 -값이면 안되는건지?
    - 그리고 여기의 이 값이 dB 로 표기를 하는게 맞긴 한건지
    - 그리고 실제 DSP 에서는 이 최대한계 리미팅을 어떻게 하는지.. 체크

"""


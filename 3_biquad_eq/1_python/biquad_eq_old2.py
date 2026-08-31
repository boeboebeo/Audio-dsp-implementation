#biquad_eq_old1.py에서는 각 계수로 impulse 실험을 해보았다면 (임의의 coefficients)
#여기서는 실제로 파라미터로 coefficients 를 도출해내서 실행해보자

#2nd-order low-pass Biquad
"""
Low-pass
   ↓
RBJ 공식 하나씩 직접 구현
   ↓
impulse response
   ↓
frequency response
    #각 filter 마다 원하는 Freq response를 만들기 위한 coefficient 공식이 다름
   ↓
cutoff 확인
   ↓
Q 변화시켜보기
   ↓
pole 확인
   ↓
r 확인
   ↓
a1/a2와 pole 관계 확인
"""

import numpy as np

def main():
    f0 = 1000       #cutoff freq
    Q = 0.707         #Quality factor (Resonance) => Q를 올리면 pole 이 unit circle 쪽으로 올라가는것 확인 가능
    fs = 48000      #sample rate
    gain = 6        #gain (dB)

    input_signal = np.zeros(fs)
    input_signal[0] = 1

    b0, b1, b2, a1, a2 = calculate_lowpass_coefficients(
                            f0, Q, fs
                            )
    output = biquad_filter_basic(
                            input_signal,
                            b0, b1, b2, a1, a2
    )
    



#계수 계산 함수

def calculate_lowpass_coefficients(f0, Q, fs):

    # 1. omega0 계산
        #RBJ 에서는 주파수를 바로 사용하지 않고, rad/sample형태로 바꿈

    w0 = 2 * np.pi * (f0/fs)    
        #한 샘플당 위상 변화량(rad/sample)

    # 2. alpha 계산

    alpha = np.sin(w0) / (2 * Q)
        #이 alpha 라는게 이렇게 특정 형태가 되는것은 
        #수학적으로 Q -> 2차 아날로그 pole -> s-domain -> bilinear trasnform -> z-domain -> alpha
        #RBJ 에서 도출해낸 Q, w0 에 의해서 결정되는 coefficient 계산용 중간 변수

    # 3. b0, b1, b2 계산
    b0 = (1 - np.cos(w0)) / 2
    b1 = 1 - np.cos(w0)
    b2 = (1 - np.cos(w0)) / 2

    # 4. a0, a1, a2 계산
    a0 = 1 + alpha
    a1 = -2 * np.cos(w0)
    a2 = 1 - alpha
        #RBJ cookbook low-pass coefficients

    # 5. a0로 normalization
    a1 = a1 / a0
    a2 = a2 / a0
    b0 = b0 / a0
    b1 = b1 / a0
    b2 = b2 / a0

    # 6. coefficient 반환
    return b0, b1, b2, a1, a2


# 필터 적용 함수

def biquad_filter_basic(input_signal, b0, b1, b2, a1, a2):
    
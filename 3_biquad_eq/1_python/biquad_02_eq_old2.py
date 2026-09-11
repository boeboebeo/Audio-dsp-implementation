#biquad_eq_old1.py에서는 각 계수로 impulse 실험을 해보았다면 (임의의 coefficients)
#여기서는 실제로 파라미터로 coefficients 를 도출해내서 실행해보자

#2nd-order low-pass Biquad
#bi-quadratic : 2차 구조를 가진 필터 
    #거의 DSP에서는 2차 IIR 필터를 가리킴
    #2차 : 최대 2샘플 전까지의 상태를 사용하는 구조
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
import matplotlib.pyplot as plt


def main():
    f0 = 1000      #cutoff freq
    Q = 5       #Quality factor (Resonance) => Q를 올리면 pole 이 unit circle 쪽으로 올라가는것 확인 가능
    fs = 48000      #sample rate
    gain = 6        #gain (dB)

    #impulse로 test 
    input_signal = np.zeros(fs) 
    input_signal[0] = 1

    b0, b1, b2, a1, a2 = calculate_lowpass_coefficients(
                            f0, Q, fs
                            )
    
    b0, b1, b2, a1, a2 = calculate_highpass_coefficients(
                            f0, Q, fs
    )

    b0, b1, b2, a1, a2 = calculate_bandpass_coefficients(
                            f0, Q, fs
    )
        #만약 Q값이 5라면 
        #20log(5) = 14dB 정도 중심주파수가 증폭됨

    output1 = biquad_filter_basic(
                            input_signal,
                            b0, b1, b2, a1, a2
    )

    b0, b1, b2, a1, a2 = calculate_bandpass2_coefficients(
                            f0, Q, fs
    )
        #Q값과 관계없이, 중심주파수가 0dB (1배 = 조절없음)
    
    output2 = biquad_filter_basic(
                            input_signal,
                            b0, b1, b2, a1, a2
    )

    comparison_BPF1_BPF2(output1, output2, fs)

    # plot_impulse_response(output, fs)
    



#계수 계산 함수
#1. low-pass
def calculate_lowpass_coefficients(f0, Q, fs):

    # 1. omega0 계산
        #RBJ 에서는 주파수를 바로 사용하지 않고, rad/sample형태로 바꿈

    w0 = 2 * np.pi * (f0/fs)    
        #한 샘플당 위상 변화량(rad/sample)

    # 2. alpha 계산
    # RBJ 계수 방법에서만 쓰이는 중간 변수 공식 = alpha

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


#2. High-pass 
def calculate_highpass_coefficients(f0, Q, fs):
    w0 = 2 * np.pi * (f0/fs)

    alpha = np.sin(w0) / (2 * Q)

    b0 = (1 + np.cos(w0)) / 2
    b1 = -(1 + np.cos(w0))
    b2 = (1 + np.cos(w0)) / 2

    a0 = 1 + alpha
    a1 = -2 * np.cos(w0)
    a2 = 1 - alpha

    #normalization 
    a1 = a1 / a0
    a2 = a2 / a0
    b0 = b0 / a0
    b1 = b1 / a0
    b2 = b2 / a0

    return b0, b1, b2, a1, a2


#3-1. Band-pass_1(Constant skirt gain BPF)
# # 중심주파수(peak)가 Q에 영향을 받아서 증폭 
def calculate_bandpass_coefficients(f0, Q, fs):
    w0 = 2 * np.pi * (f0/fs)

    alpha = np.sin(w0) / (2 * Q)

    b0 =   np.sin(w0)/2  # =   Q*alpha
    b1 =   0
    b2 =  -np.sin(w0)/2  # =  -Q*alpha
    a0 =   1 + alpha
    a1 =  -2 * np.cos(w0)
    a2 =   1 - alpha

    #normalization 
    a1 = a1 / a0
    a2 = a2 / a0
    b0 = b0 / a0
    b1 = b1 / a0
    b2 = b2 / a0

    return b0, b1, b2, a1, a2

#3-2. Band-pass_2(Constant 0dB peak gain)
# 중심주파수(peak)값을 0dB 로 유지함 
def calculate_bandpass2_coefficients(f0, Q, fs):
    w0 = 2 * np.pi * (f0/fs)

    alpha = np.sin(w0) / (2 * Q)

    b0 =   alpha
    b1 =   0
    b2 =  -alpha
    a0 =   1 + alpha
    a1 =  -2*np.cos(w0)
    a2 =   1 - alpha

    #normalization 
    a1 = a1 / a0
    a2 = a2 / a0
    b0 = b0 / a0
    b1 = b1 / a0
    b2 = b2 / a0

    return b0, b1, b2, a1, a2


# 필터 적용 함수
def biquad_filter_basic(input_signal, b0, b1, b2, a1, a2):
    #각 샘플 계산

    #x, y 값 초기화 (for문 밖에서)
    x1 = 0.0
    x2 = 0.0
    y1 = 0.0
    y2 = 0.0

    #input 길이 만큼의 output 배열 생성
    output = [0.0] * len(input_signal)

    for n, x0 in enumerate(input_signal):
        y0 = b0*x0 + b1*x1 + b2*x2 - a1*y1 - a2*y2

        output[n] = y0

        #state update
        x2 = x1
        x1 = x0
        y2 = y1
        y1 = output[n]

    return output


#impulse response check 함수
def plot_impulse_response(output, fs):
    spectrum = np.fft.rfft(output)
    magnitude = np.abs(spectrum)
    mag_db = 20 * np.log10(magnitude + 1e-12)

    #fft 간격
    fft_freq = np.fft.rfftfreq(len(output), 1/fs)

    plt.plot(fft_freq[1:], mag_db[1:])
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude (dB)")
    plt.xscale("log")
    plt.xlim(20, 40000)
    plt.ylim(-60, 20)
    plt.tight_layout()
    plt.show()


#comparison : BPF1 vs BPF2
def comparison_BPF1_BPF2(output1, output2, fs):
    fig, axes = plt.subplots(1, 2, figsize=(10, 8))

    ax = axes[0]

    spectrum = np.fft.rfft(output1)
    magnitude = np.abs(spectrum)
    mag_db = 20 * np.log10(magnitude + 1e-12)

    fft_freq = np.fft.rfftfreq(len(output1), (1/fs))


    ax.plot(fft_freq[1:], mag_db[1:])
    ax.set_title("BPF1 : Constant skirt gain BPF")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Magnitude (dB)")
    ax.set_xlim(20, 20000)
    ax.set_ylim(-60, 20)
    ax.set_xscale("log")


    ax = axes[1]

    spectrum = np.fft.rfft(output2)
    magnitude = np.abs(spectrum)
    mag_db = 20 * np.log10(magnitude + 1e-12)

    fft_freq = np.fft.rfftfreq(len(output2), (1/fs))


    ax.plot(fft_freq[1:], mag_db[1:])
    ax.set_title("BPF2 : Constant 0dB peak gain")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Magnitude (dB)")
    ax.set_xlim(20, 20000)
    ax.set_ylim(-60, 20)
    ax.set_xscale("log")


    plt.tight_layout()
    plt.show()
    



if __name__ == "__main__":
    main()
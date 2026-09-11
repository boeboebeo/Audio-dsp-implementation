"""class EQ 로 전체 묶어주기

"""

import numpy as np
import matplotlib.pyplot as plt

fs = 48000


#Low pass 
def calculate_lowpass_coefficients(w0, alpha):
    b0 =  (1 - np.cos(w0))/2
    b1 =   1 - np.cos(w0)
    b2 =  (1 - np.cos(w0))/2
    a0 =   1 + alpha
    a1 =  -2*np.cos(w0)
    a2 =   1 - alpha

    return b0, b1, b2, a0, a1, a2

#high pass 
def calculate_highpass_coefficients(w0, alpha):
    b0 =  (1 + np.cos(w0))/2
    b1 = -(1 + np.cos(w0))
    b2 =  (1 + np.cos(w0))/2
    a0 =   1 + alpha
    a1 =  -2*np.cos(w0)
    a2 =   1 - alpha

    return b0, b1, b2, a0, a1, a2

#BPF (constant 0dB peak gain)
def calculate_bandpass_coefficients(w0, alpha):
    b0 =   alpha
    b1 =   0
    b2 =  -alpha
    a0 =   1 + alpha
    a1 =  -2*np.cos(w0)
    a2 =   1 - alpha

    return b0, b1, b2, a0, a1, a2

#Band reject (= notch)
def calculate_notch_coefficients(w0, alpha):
    b0 =   1
    b1 =  -2*np.cos(w0)
    b2 =   1
    a0 =   1 + alpha
    a1 =  -2*np.cos(w0)
    a2 =   1 - alpha

    return b0, b1, b2, a0, a1, a2

#Peak 
def calculate_peaking_coefficients(w0, alpha, A):
    b0 =   1 + alpha*A
    b1 =  -2*np.cos(w0)
    b2 =   1 - alpha*A
    a0 =   1 + alpha/A
    a1 =  -2*np.cos(w0)
    a2 =   1 - alpha/A

    return b0, b1, b2, a0, a1, a2

#lowshelf
def calculate_lowshelf_coefficients(w0, alpha, A, sqrt_A):
    b0 =    A*( (A+1) - (A-1)*np.cos(w0) + 2*sqrt_A*alpha )
    b1 =  2*A*( (A-1) - (A+1)*np.cos(w0)                  )
    b2 =    A*( (A+1) - (A-1)*np.cos(w0) - 2*sqrt_A*alpha )
    a0 =        (A+1) + (A-1)*np.cos(w0) + 2*sqrt_A*alpha
    a1 =   -2*( (A-1) + (A+1)*np.cos(w0)                  )
    a2 =        (A+1) + (A-1)*np.cos(w0) - 2*sqrt_A*alpha
    
    return b0, b1, b2, a0, a1, a2


#highshelf
def calculate_highshelf_coefficients(w0, alpha, A, sqrt_A):
    b0 =    A*( (A+1) + (A-1)*np.cos(w0) + 2*sqrt_A*alpha )
    b1 = -2*A*( (A-1) + (A+1)*np.cos(w0)                  )
    b2 =    A*( (A+1) + (A-1)*np.cos(w0) - 2*sqrt_A*alpha )
    a0 =        (A+1) - (A-1)*np.cos(w0) + 2*sqrt_A*alpha
    a1 =    2*( (A-1) - (A+1)*np.cos(w0)                  )
    a2 =        (A+1) - (A-1)*np.cos(w0) - 2*sqrt_A*alpha

    return b0, b1, b2, a0, a1, a2




class Band:
    def __init__(self, f0, Q, gain, filter_type):

        self.f0 = f0
        self.Q = Q
        self.gain = gain
        self.filter_type = filter_type

        #state 도 여기서 초기화
        self.x1 = 0.0
        self.x2 = 0.0
        self.y1 = 0.0
        self.y2 = 0.0

        #계수값 초기화 (공간을 미리 만들어둠)
        self.b0 = 0.0
        self.b1 = 0.0
        self.b2 = 0.0
        self.a0 = 0.0
        self.a1 = 0.0
        self.a2 = 0.0

        #내부에서 그냥 Band 생성시 -> 바로 계수 계산하도록 처리해버림
        #근데 나중에 사용자가 f0, Q, gain 등을 변경한다면 다시 계수를 계산해야함
        #그래서 아래에 set_f0.. 등의 함수가 생겨난것!
        self.calculate_coefficients()

    def set_f0(self, f0):
        self.f0 = f0
        self.calculate_coefficients()

    def set_Q(self, Q):
        self.Q = Q
        self.calculate_coefficients()

    def set_gain(self, gain):
        self.gain = gain
        self.calculate_coefficients()

    def set_filter_type(self, filter_type):
        self.filter_type = filter_type
        self.calculate_coefficients()



    def calculate_coefficients(self):
        #cal.. (self, f0, Q, gain, filter_type) -> 이렇게 받아올 필요없음
        #그냥 내부에서 self.f0 로 쓰면 된다.
        #걍 cal.. (self) -> 이러면 __init__ 의 변수값들 불러 올 수 있음

        #1. 내 f0, Q 로 w0, alpha 계산해야함
        w0 = 2 * np.pi * (self.f0/fs)
        alpha = np.sin(w0) / (2 * self.Q)

        A = 10 ** (self.gain/40)
        sqrt_A = np.sqrt(A)

        #2. 내가 어떤 filter_type 인지 확인해야함
        if self.filter_type == "lowpass":
            b0, b1, b2, a0, a1, a2 = calculate_lowpass_coefficients(w0, alpha)

        elif self.filter_type == "highpass":
            b0, b1, b2, a0, a1, a2 = calculate_highpass_coefficients(w0, alpha)

        elif self.filter_type == "bandpass":
            b0, b1, b2, a0, a1, a2 = calculate_bandpass_coefficients(w0, alpha)

        elif self.filter_type == "notch":
            b0, b1, b2, a0, a1, a2 = calculate_notch_coefficients(w0, alpha)

        elif self.filter_type == "peaking":
            b0, b1, b2, a0, a1, a2 = calculate_peaking_coefficients(w0, alpha, A)

        #normalization
        b0 /= a0
        b1 /= a0
        b2 /= a0
        #a0 /= a0 <= 이걸 먼저 normalization 해버리면 밑의 정규화에 문제생김
        a1 /= a0
        a2 /= a0
        a0 = 1.0

        self.b0 = b0
        self.b1 = b1
        self.b2 = b2
        self.a0 = a0
        self.a1 = a1
        self.a2 = a2
        

    def process(self, input_signal):
        output = [0.0] * len(input_signal)

        for n, x0 in enumerate(input_signal):
            
            y0 = (
                self.b0 * x0
                + self.b1 * self.x1
                + self.b2 * self.x2
                - self.a1 * self.y1
                - self.a2 * self.y2 
            )

            output[n] = y0

            self.x2 = self.x1
            self.x1 = x0
            self.y2 = self.y1
            self.y1 = y0
            # x0은 현재 buffer 에서 현재 처리중인 샘플 (지역변수), 
            # y0은 현재 샘플을 계산해서 방금 만든 결과값이라서 지역변수 => 이 둘은 이번 계산에서만 필요한 임시변수 
            # 둘다 그러한 이유로 어디서 불러오는 값이 아님 => 다음 계산에서도 기억해야 함
            # (그래서 Band 객체 안에 초기화 해서 저장해둔 것)

        return output 



#input signal
input_signal = np.zeros(fs)
input_signal[0] = 1


# #여기가 위의 Band class 사용하는 코드
# band1 = Band(f0=10000, Q=0.707, gain=6, filter_type = "lowpass")
#     #class Band 정의보다 이 함수가 위에 있으면 안됨
# band1.calculate_coefficients()
# output1 = band1.process(input_signal)

# band2 = Band(f0=50, Q=0.707, gain=6, filter_type = "highpass")
# band2.calculate_coefficients()
# output2 = band2.process(output1)

# band3 = Band(f0=1000, Q=0.707, gain=10, filter_type="peaking")
# band3.calculate_coefficients()
# output3 = band3.process(output2)




class EQ:
    def __init__(self):
        self.bands = []

    #self.bands라는 배열안에 band 를 추가
    def add_band(self, band):
        self.bands.append(band)

        #self.bands = [band1, band2, ...] //이렇게 채워지게 됨

    #class Band 내부의 process에서는 실제 필터 연산을 함
    #class EQ 내부의 아래의 process 에서는 band 내부의 함수로 처리시킴
    def process(self, input_signal):
        output = input_signal

        for band in self.bands:
            output = band.process(output)

        return output 



#여기가 사용코드

band1 = Band(
    f0 = 100,
    Q = 1.0,
    gain = 0,
    filter_type = "highpass"
)

band2 = Band(
    f0=1000,
    Q=1.0,
    gain=6,
    filter_type="peaking"
)

band3 = Band(
    f0 = 10000,
    Q=1.0,
    gain = 0,
    filter_type = "lowpass"
)

#EQ class 로 하나의 객체를 만듦
eq = EQ()

#coefficietns 계산
# band1.calculate_coefficients()
# band2.calculate_coefficients()
# band3.calculate_coefficients()

#각 band 를 eq 안에 넣기
eq.add_band(band1)
eq.add_band(band2)
eq.add_band(band3)

output = eq.process(input_signal)




#여기서부터 분석 코드 - 시각화
def plot_response(input_signal, output, fs):
    fig, axes = plt.subplots(1, 2, figsize=(12, 8))

    #input_plot
    ax = axes[0]

    spectrum = np.fft.rfft(input_signal)
    magnitude = np.abs(spectrum)
    mag_db = 20 * np.log10(magnitude + 1e-12)

    fft_freq = np.fft.rfftfreq(len(input_signal), (1/fs))

    ax.plot(fft_freq[1:], mag_db[1:])
    ax.set_ylim(-20, 20)
    ax.set_xscale("log")
    ax.set_xlim(20, 20000)


    #output_plot
    ax = axes[1]
    spectrum = np.fft.rfft(output)
    magnitude = np.abs(spectrum)
    mag_db = 20 * np.log10(magnitude + 1e-12)

    fft_freq = np.fft.rfftfreq(len(output), (1/fs))

    ax.plot(fft_freq[1:], mag_db[1:])
    ax.set_ylim(-20, 20)
    ax.set_xscale("log")
    ax.set_xlim(20, 20000)

    plt.tight_layout()
    plt.show()

plot_response(input_signal, output, fs)
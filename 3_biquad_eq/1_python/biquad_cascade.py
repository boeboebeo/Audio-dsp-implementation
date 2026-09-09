# Filter 를 여러개 연결 = cascade

""" 결국 x(input) -> H1 -> H2 -> H3 -> y(output)

이렇게 구조를 짠다는 것은 

H1의 출력을 H2의 입력으로 넣어서 filtering 하고,
H2의 출력을 H3의 입력으로 넣어서 출력을 만드는 것이다. 

Y(z) = X(z) * H1(z) * H2(z) * H3(z)

    아래와 같은 구조가 된다. 
    output1 = filter1(input_signal)
    output2 = filter2(output1)
    output3 = filter3(output2)
        
    => 근데 이게 8개의 band 를 가지게 된다면 다 일일이 쓰기 귀찮으므로,
        for 문으로 각 band 를 처리

    #이렇게 처리하게 됨
    output = input_signal

    for band in bands:
        output = band.process(output)

        //output 이라는 변수를 계속 갱신하면서 연산에 사용함
        //각 band 는 자기만의 f0, Gain, Q 를 가지고 있음


    **각 필터타입에 따라서 계수를 구하는 def 설계해두고,
    **각각의 band 마다 if/elif 로 어떤 coefficient 함수를 호출할지 설정함

"""


import numpy as np
import matplotlib.pyplot as plt


def main():
    fs = 48000
    Q = 0.707
    f0 = 1000 
    gain = 2 #dB
    A = 10 ** (gain/40)
    sqrt_A = np.sqrt(A)

    input_signal = np.zeros(fs)
    input_signal[0] = 1


    w0 = 2 * np.pi * (f0/fs)
    alpha = np.sin(w0) / (2 * Q)


    b0, b1, b2, a0, a1, a2 = calculate_highshelf_coefficients(w0, alpha, A, sqrt_A)

    b0, b1, b2, a0, a1, a2 = normalize_coefficients(
        b0, b1, b2, a0, a1, a2
    )

    output = biquad_filter_basic(input_signal, b0, b1, b2, a1, a2)


    plot_response(input_signal, output, fs)

    




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



#normalization 하는 함수
def normalize_coefficients(b0, b1, b2, a0, a1, a2):

    b0 /= a0
    b1 /= a0
    b2 /= a0
    a1 /= a0
    a2 /= a0

    return b0, b1, b2, a0, a1, a2
    



#filter processing
def biquad_filter_basic(input_signal, b0, b1, b2, a1, a2):
    
    #상태값 초기화
    x1 = 0
    x2 = 0
    y1 = 0
    y2 = 0

    #출력 배열 만들기
    output = [0.0] * len(input_signal)


    for n, x0 in enumerate(input_signal):
        y0 = b0*x0 + b1*x1 + b2*x2 - a1*y1 - a2*y2

        output[n] = y0

        #state 처리
        x2 = x1
        x1 = x0
        y2 = y1
        y1 = output[n]

    return output


def plot_response(input_signal, output, fs):
    fig, axes = plt.subplots(1, 2, figsize = (12, 8))

    #before filtering 
    ax = axes[0]

    spectrum = np.fft.rfft(input_signal)
    magnitude = np.abs(spectrum)
    mag_db = 20 * np.log10(magnitude + 1e-12)
        #위 계산을 하면 20log(1) = 0 이 나옴
        #즉 magnitude = 1 <=> 0dB 와 동일
        #그러므로, before filtering 에서의 형태가 0dB 직선이 나옴

    fft_freq = np.fft.rfftfreq(len(input_signal), (1/fs))

    ax.plot(fft_freq[1:], mag_db[1:])
    ax.set_title("before filtering")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Magnitude (dB)")
    ax.set_ylim(-3, 3)
    ax.set_xscale("log")




    #after filtering 
    ax = axes[1]

    spectrum = np.fft.rfft(output)
    magnitude = np.abs(spectrum)
    mag_db = 20 * np.log10(magnitude + 1e-12)



    ax.plot(fft_freq[1:], mag_db[1:])
    ax.set_title("after filtering")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Magnitude (dB)")
    ax.set_ylim(-3, 3)
    ax.set_xscale("log")


    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()



"""A & sqrt(..) ?

1) A란 (RBJ 공식에서의 중간 변수 중 하나)

A = np.sqrt(10^(dBgain / 20))
  =         10^(dBgain / 40)

    ** A 또한 RBJ 에서 필터설계를 위해 정의한 변수
        
            //이렇게 우선 구조를 짜서 아래에서 A가 이렇게 나오게 됨
        2) A^2 = 10^(dB/20)
        3) A = 10^(dB/40)

        // 이것 또한 alpha 와 같이 RBJ 에서 정의한 중간변수 


2) sqrt() 함수의 기능

    **sqrt() : 제곱근(root)를 구하는 함수
    ex. sqrt(0.81) = 루트(0.81) = 0.9
        // 복소수 에서 원점에서 pole 까지의 거리를 구할때도 sqrt()가 사용됨
        : r = 루트( (real)^2 + (imag)^2 ) 
"""
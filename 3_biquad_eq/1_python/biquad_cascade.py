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
    A = ..?

    w0 = 2 * np.pi * (f0/fs)
    alpha = np.sin(w0) / 2 * Q


def calculate_lowpass_coefficients(fs, f0, Q, w0, alpha):
    b0 =  (1 - np.cos(w0))/2
    b1 =   1 - np.cos(w0)
    b2 =  (1 - np.cos(w0))/2
    a0 =   1 + alpha
    a1 =  -2*np.cos(w0)
    a2 =   1 - alpha

    #normalization
    b0 /= a0
    b1 /= a0
    b2 /= a0
    a1 /= a0
    a2 /= a0

    return b0, b1, b2, a1, a2

#Low pass 
def calculate_lowpass_coefficients(fs, f0, Q, w0, alpha):
    b0 =  (1 - np.cos(w0))/2
    b1 =   1 - np.cos(w0)
    b2 =  (1 - np.cos(w0))/2
    a0 =   1 + alpha
    a1 =  -2*np.cos(w0)
    a2 =   1 - alpha

    return b0, b1, b2, a1, a2

#high pass 
def calculate_highpass_coefficients(fs, f0, Q, w0, alpha):
    b0 =  (1 + np.cos(w0))/2
    b1 = -(1 + np.cos(w0))
    b2 =  (1 + np.cos(w0))/2
    a0 =   1 + alpha
    a1 =  -2*np.cos(w0)
    a2 =   1 - alpha

    return b0, b1, b2, a1, a2

#BPF (constant 0dB peak gain)
def calculate_bandpass_coefficients(fs, f0, Q, w0, alpha):
    b0 =   alpha
    b1 =   0
    b2 =  -alpha
    a0 =   1 + alpha
    a1 =  -2*np.cos(w0)
    a2 =   1 - alpha

    return b0, b1, b2, a1, a2

#Band reject (= notch)
def calculate_notch_coefficients(fs, f0, Q, w0, alpha):
    b0 =   1
    b1 =  -2*np.cos(w0)
    b2 =   1
    a0 =   1 + alpha
    a1 =  -2*np.cos(w0)
    a2 =   1 - alpha

    return b0, b1, b2, a1, a2

#Peak 
def calculate_peaking_coefficients(fs, f0, Q, w0, alpha, A):
    b0 =   1 + alpha*A
    b1 =  -2*np.cos(w0)
    b2 =   1 - alpha*A
    a0 =   1 + alpha/A
    a1 =  -2*np.cos(w0)
    a2 =   1 - alpha/A

    return b0, b1, b2, a1, a2

#lowshelf
def calculate_lowshelf_coefficients(fs, f0, Q, w0, alpha, A):
    b0 =    A*( (A+1) - (A-1)*np.cos(w0) + 2*sqrt(A)*alpha )
    b1 =  2*A*( (A-1) - (A+1)*np.cos(w0)                   )
    b2 =    A*( (A+1) - (A-1)*np.cos(w0) - 2*sqrt(A)*alpha )
    a0 =        (A+1) + (A-1)*np.cos(w0) + 2*sqrt(A)*alpha
    a1 =   -2*( (A-1) + (A+1)*np.cos(w0)                   )
    a2 =        (A+1) + (A-1)*np.cos(w0) - 2*sqrt(A)*alpha
    
    return b0, b1, b2, a1, a2

#highshelf
def calculate_highshelf_coefficients(fs, f0, Q, w0, alpha, A):
    b0 =    A*( (A+1) + (A-1)*np.cos(w0) + 2*np.sqrt(A)*alpha )
    b1 = -2*A*( (A-1) + (A+1)*np.cos(w0)                   )
    b2 =    A*( (A+1) + (A-1)*np.cos(w0) - 2*sqrt(A)*alpha )
    a0 =        (A+1) - (A-1)*np.cos(w0) + 2*sqrt(A)*alpha
    a1 =    2*( (A-1) - (A+1)*np.cos(w0)                   )
    a2 =        (A+1) - (A-1)*np.cos(w0) - 2*sqrt(A)*alpha

    return b0, b1, b2, a1, a2


"""A & sqrt(..) ?

1) A란 (RBJ 공식에서의 중간 변수 중 하나)

A = np.sqrt(10^(dBgain / 20))
  =         10^(dBgain / 40)

    **A^2 에서 파생... 왜 A^2 인거지?

    - A = 10^(6/40)



2) sqrt() 함수의 기능

    **sqrt() : 제곱근(root)를 구하는 함수
    ex. sqrt(0.81) = 루트(0.81) = 0.9
        // 복소수 에서 원점에서 pole 까지의 거리를 구할때도 sqrt()가 사용됨
        : r = 루트( (real)^2 + (imag)^2 ) 
"""

#normalization 하는 함수
def normalize_coefficients(b0, b1, b2, a0, a1, a2):

    b0 /= a0
    b1 /= a0
    b2 /= a0
    a1 /= a0
    a2 /= a0

    return b0, b1, b2, a1, a2
    

#filter processing
def biquad_filter_basic(b0, b1, b2, a1, a2):
    

    #state 처리
    x2 = x1
    x1 = x0
    y2 = y1
    y1 = 

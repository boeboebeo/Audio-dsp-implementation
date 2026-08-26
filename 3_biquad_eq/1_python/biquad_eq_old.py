#biquad EQ - 2차 IIR 구조 
    #관계 : Butterworth 필터와 같은 타입을 biquad 들로 구현할 수 있다
    #Butterworth 와 같은 종류는 어떤 주파수 응답을 만들것인가
"""need to know 
1)filter topologies 
2)calculate coefficients 

biquad 에서 제일중요한건 "계수"와 "상태(state)"
using RBJ Cookbook

① difference equation 적기
        ↓
② x1, x2, y1, y2 상태 만들기
        ↓
③ b0~b2, a1~a2 계수 만들기
        ↓
④ sample 하나 처리
        ↓
⑤ state 업데이트
        ↓
⑥ for loop
        ↓
⑦ impulse 테스트
        ↓
⑧ coefficient 계산 추가
        ↓
⑨ cutoff / Q / gain 연결
        ↓
⑩ frequency response 확인

"""

#내가 짠 구조
def basic_2nd_IIR_structure():
    input_signal = [0, 0, 0, 0, 0, 0, 0]
    input_signal[0] = 1
    x = input_signal 

    output_signal = [0, 0, 0, 0, 0, 0, 0]
    y = output_signal

    #초기 state 
    x1 = 0
    x2 = 0
    y1 = 0 #y[n-1]
    y2 = 0 #y[n-2]

    #coefficients
    b0 = 0.2
    b1 = 1.5
    b2 = 0.9
    a1 = 1.3
    a2 = 0.3
        #a0은 정규화 과정에서 1로 없앰 

    #input index 와 진폭값 따로 가지고 오기 
    for n, value in enumerate(x):
        x0 = value

        #difference equation 
        y[n] = b0*x0 + b1*x1 + b2*x2 - a1*y1 - a2*y2

        #state update
        x2 = x1 #x2 를 먼저 업데이트 해야 순서가 맞음
        x1 = x0
        y2 = y1
        y1 = y[n] 

        print(y)
 
input_signal = [1, 0, 0, 0, 0, 0]

#coefficients
b0 = 0.2
b1 = 1.5
b2 = 0.9
a1 = 1.3
a2 = 0.3


#깔끔하게 정리한 구조
def biquad_filter_basic(input_signal, b0, b1, b2, a1, a2):
    output = [0.0] * len(input_signal)

    x1 = 0.0
    x2 = 0.0
    y1 = 0.0
    y2 = 0.0

    for n, x0 in enumerate(input_signal):
        y0 = b0*x0 + b1*x1 + b2*x2 - a1*y1 - a2*y2
        
        output[n] = y0

        x2 = x1
        x1 = x0
        y2 = y1
        y1 = y0

        print([round(v, 6) for v in output])

    return output


biquad_filter_basic(input_signal, b0, b1, b2, a1, a2)


#def calculate_coefficients():

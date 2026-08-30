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

import numpy as np



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
 

def main():
    input_signal = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    #coefficients
    b0 = 3.0
    b1 = 3.9
    b2 = 2.5
    a1 = 1.2
    a2 = 1.0
    """
    b, a coefficients 실험 log

    1)b0, b1, b2 의 값을 키워도 결국 impulse response 의 진폭은 점점 작아지지만
        - b 는 입력값에 곱해지는 계수
    2)a1, a2의 값들은 키우면 점점 impulse response 의 진폭이 시간이 지나면서 커짐
        - a 는 출력값에 곱해지는 계수 
        => feedback 과 관련이 있는 계수이다.
    """
    print(input_signal)

    biquad_filter_basic(input_signal, b0, b1, b2, a1, a2)
    check_stability(a1, a2)





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

def check_stability(a1, a2):
    #Pole 은 unit circle 안에 있어야 안정적 (<1)
    #우선 H(z)수식 -> Pole 을 구하기

    poles = np.roots([1, a1, a2])
        #np.roots : 다항식(polynomial)의 근(root)을 구해주는 함수 
        #[1, a1, a2]는 -> z^2 + a1*z^1 + a2 의 이차방정식

    #학습용
    # if np.all(np.abs(poles) < 1) :
    #     print(f"stability check ✅. poles: {poles}")
    # else:
    #     print(f"not stability ❌. poles: {poles}")

    #실사용용
    stable = np.all(np.abs(poles) < 1)

    print(f"poles : {poles}")
    print(f"stable : {stable}")

    #poles가 [-0.6+0.8j -0.6-0.8j] 이렇게 나옴
    #-0.6 은 실수부, +0.8j 는 허수부 
    #|z| = 루트( (0.6)^2 + (0.8)^2 ) 
         # 루트 (0.36 + 0.64) = 1 
         # |z| = 1. 따라서 poles 는 안정적이지 않음

    #나중에 다른 코드에서 사용하려면 true/false 를 반환하는 것이 유용함
    return stable  #true or false 값 반환

"""a1, a2 와 pole 의 관계

1) z-transform할 경우
    : z^2 + a1*z + a2 = 0이 되고,

    2차 방정식 근과 계수와의 관계에 의해
    p1 + p2 = -a1
    p1 * p2 = a2 

2) example

poles : [-0.6+0.8j -0.6-0.8j] 일 경우에

p1 + p2 = -1.2 
p1 * p2 = 복소켤레끼리 곱 (복소켤레 : 허수부의 부호를 반대로 바꾸는 것) : p, p*가 복소켤레 표시
        = (-0.6)^2 + (0.8)^2 = 1

    즉, a1 = 1.2, a2 = 1

    => z^2 + 1.2z + 1 (이 식이 pole pair에 대응하는 denominator)

3) 복소켤레 pole 을 각각 
p = re^(jθ), p* = re^(-jθ)라고 한다면

p + p* = 2rcosθ
pp* = r^2 (Euler)

"""




#def calculate_coefficients():


if __name__ == "__main__":
    main()
// main.cpp : 실행 및 테스트를 담당 (Implementation. 구현)

// std:: -> standard(표준 라이브러리)


// (1) 라이브러리 (include): import numpy as np 와 동일한 구조
#include <vector>   // python 의 list, numpy array 와 유사한 컨테이너 -> 크기가 달라질수있는 배열
#include <cmath>    // std::sin() 에서 사용 - python 의 math.sin() 과 유사
                    // sin, cos, log 사용시
#include <random>   // std::random_device
#include <iostream> // std::cout <- python 의 print() 와 유사, print
                    // print(x) = std::cout <<x ;
#include <iomanip>  // std::setprecision (콘솔 출력 소수점 자리수 맞추기용)
                    // std::setprecision(3) 이면 1.234567이 1.235 처럼 출력됨
                    // 출력 자리수

#include "Gain.h"   // 내가 만든 파일을 가지고옴. 만약 Gain.h 파일 안에 class Gain { ..} 이 들어있다면
                    // main.cpp 에서는 #include "Gain.h" 만으로 위의 파일에서의 Gain 클래스를 사용할 수 있다.
#include "WavWriter.h"



// (2) 함수 정의_createSine(): python 의 def create_sine(): 과 동일한 구조
// std::vector<float> createSine(double..) { .. return buffer}
// == create_sine(fs, freq, duration): .. return 과 완전히 동일하다

std::vector<float> createSine (double sampleRate, double frequency, double durationSeconds)
//std::vector<float>을 반환 타입으로 쓰는 이유 : Python의 numpy array 에 대응하는 
//C++ 표준 라이브러리의 "크기가 자유롭게 늘어나는" 배열
//std::vector<float> : float 만 저장하는 vector. python 은 여러 문자열을 같이 저장할 수 있지만 여기서는 안됨
//c++ 에서는 무조건 자료형을 같이 적어줘야 함 ex. double sampleRate (python 에서는 알아서 다 판단했었다)
// double? : 

{
    const int numSamples = static_cast<int> (sampleRate * durationSeconds);
        // const int numSamples : 절대 바뀌지 않는 변수값 'const'
        // <int>(..) : 는 뒤 괄호안 값이 소수점이 나와도 int 로 변환하라는 뜻 
        // 샘플의 개수는 소수점이 나올 수 없으니까 ex. 48000.3 같은건 나올 수 없음
    std::vector<float> buffer (static_cast<size_t> (numSamples));
        //numSamples 크기의 buffer 라는 vector (배열)을 만들어라
        //vector 는 크기를 : size_t라는 형으로 받음 
        // 위에서의 sampleRate = 48000.0 이고 duration = 1.5 라면 48000.0 * 1.5 = 72000.0 가 나오게 된다 (이건 double)
        // 그래서 그 double 을 static_cast<int> 로 변환해서 정수로 바꿈 (c++은 자료형의 변경이 안되기 때문에 이걸 써서 자료형을 변화줘야함)
        // static : 정적인, 안전한 , cast : 형 변환(type conversion)
        // double : 소수(실수)를 저장하는 자료형. float 보다 더 높은 precision(정밀도)를 가짐

    for (int i = 0; i < numSamples; ++i)
    {
        const double t = static_cast<double> (i) / sampleRate;
        buffer[static_cast<size_t> (i)] = static_cast<float> (std::sin (2.0 * M_PI * frequency * t));
    }

    return buffer;
}


// (2) 함수 정의_createWhiteNoise() 



// (3) Gain 적용 함수_applyGainAndSave() : def apply_gain(): 과 동일한 구조




// (4) main()


// (5) 프로그램 종료 : python 의 if __name__ =="__main__": 과 동일한 구조



/* 입력부터 -> 출력까지의 전체 과정

사용자가 입력 
↓
sampleRate = 48000.0 (double) -> 계산 오차를 줄이기 위해서 double 사용
frequency = 200.0 (double)
duration = 1.0 (double)
↓
double 로 시간(t) 계산 (or sine 계산 or phase 계산)
    t = i / sampleRate
↓
double 로 sin() 계산
    sin(2pift)
↓
결과를 float 로 변환
    static_cast<float>()
↓
vector<float> 에 저장 -> 오디오는 float을 가장 많이 사용함
    buffer
↓
return buffer


    1) float : 소수(실수) - 4 Byte (약 소수점 7자리)
        ex. float a = 3.1415926f;
        float 뒤에는 f 가 붙게 되는데, 이 숫자는 float 입니다. 하는 코드
    2) double : 소수(실수) - 8 Byte (약 소수점 15-16자리)
        ex. double b = 3.141592653589793;
        double 뒤에는 f가 안붙음. f 가 안붙어있는 실수는 double 이다.

=> 계산은 double(정확도), 저장은 float(메모리와 성능)

! 참고로 int 는 정수 
*/
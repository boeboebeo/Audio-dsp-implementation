// main.cpp : 실행 및 테스트를 담당 (Implementation. 구현)

// std:: -> standard(표준 라이브러리) <- std::__ 여기 자리에 붙는건 namespace. ex. std::sin()
// cmath , random 은 헤더 이름! 
// std::vector는 vector 라는 헤더이름에서 vector 라는 기능을 사용함
// std::sin()는 cmath 라는 헤더이름에서 sin() 기능을 사용함
// std::max(), juce::jmax(), myMath::max() 처럼 앞에 서로 다른 네임스페이스 안에 존재함


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
//std::vector<float>이 반환 타입 -> vector<float> 쓰는 이유 : Python의 numpy array 에 대응하는 
//C++ 표준 라이브러리의 "크기가 자유롭게 늘어나는" 배열
//std::vector<float> : float 만 저장하는 vector. python 은 여러 문자열을 같이 저장할 수 있지만 여기서는 안됨
//c++ 에서는 무조건 자료형을 같이 적어줘야 함 ex. double sampleRate (python 에서는 알아서 다 판단했었다)
// double? : 소수/실수형 (좀더 많은 자리수까지 표현)

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

    for (int i = 0; i < numSamples; ++i)    // 여기 ++i 가 1씩 키워줌 (반복후 1키움)
                                            // i = i + 1 (= ++i)
        // for 문의 구조는 for (초기화; 조건; 증가)
        // { 실행 }
    {
        const double t = static_cast<double> (i) / sampleRate; // 현재의 샘플 번호 i 를 double 형으로 바꿔서 /48000 함 -> time 계산
        buffer[static_cast<size_t> (i)] = static_cast<float> (std::sin (2.0 * M_PI * frequency * t));
            //buffer[i] : buffer vector 에 접근
            //size_t = 배열의 인덱스 전용 자료형
            // 여기서는 buffer 라는 vector의 index 값의 자리에다가 sine 계산해서 진폭값 저장
            // M_PI = pi (3.141592....)
    }

    return buffer; 
    // buffer 라는 vector 안에 각 t에서 계산된 사인파의 진폭값이 순서대로 저장되어 있음
}


// (2) 함수 정의_createWhiteNoise() 
std::vector<float> createWhiteNoise(double sampleRate, double durationSeconds)
{
    const int numSamples = static_cast<int> (sampleRate * durationSeconds);
    std::vector<float> buffer (static_cast<size_t> (numSamples));

    std::random_device rd;
        // random device : 매번 다른 값을 하나 가져옴 (랜덤한 seed 값)
        // ex. 84372918, 1234 ..등의 값을 가지고 옴 
        // random_device 라는 클래스(설계도)로 만든 객체(변수) : rd
    std::mt19937 engine (rd()); 
        // Mersenne Twister : mt19937. random 값 만들어내는 엔진
        // mt19937 engine(1234); <- 위의 rd; 에서 가지고 온 값 
    std::uniform_real_distribution<float> distribution (-1.0f, 1.0f);
        // 어떤 범위의 Random 값을 만들 것인지 여기서는 -1.0 ~ 1.0 범위
        // 결과를 float 형으로 만듦

    for (int i = 0; i < numSamples; ++i) //초기화; 조건; 반복 후 마다 +1추가
    buffer[static_cast<size_t> (i)] = distribution (engine);
        // buffer[i] 의 인덱스 위치에 distribution(engine) 계산해서 넣음
        // distribution : 함수처럼 동작하는 객체 (Function Object)
        // 총 흐름 : engine 에게 random 값 하나 뽑아달라고 시키고, 그 결과를 distribution 규칙(-1~1)에 맞게 변환해서 반환한다.

    return buffer;
}




// (3) Gain 적용 함수_applyGainAndSave() : def apply_gain(): 과 동일한 구조
// void 는 반환하는 값이 없다는 뜻 ex. int add(...) 면 int 값을 반환하는데, void는 출력만하고 return;할 값 없음
// Wave 파일 저장만 하고, 어떤 값을 돌려주지는 않아서 void 사용한 것 
void applyGainAndSave (const std::vector<float>& inputWave, //const : 값 못 바꾸므로 곧 읽기 전용이라는 뜻, 입력버퍼 보호를 위함
                                                // & inputWave : &(참조) -> inputWave 벡터 전체를 그대로 사용(복사는 오래걸리므로)
                                                // & + const : 원본을 복사없이 읽기만 함 (복사못함)
                        const std::string& waveName, //이름도 그대로 빌려옴
                        float linearMagnitude,
                        bool invert, // 여기서는 위상반전 따로 적용
                                     // true: 위상반전, false: 그대로 출력
                        double sampleRate)

        // = 입력 오디오버퍼(inputWave)를 그대로 읽어와서 이름 저장, magnitude만큼 게인 적용,
        // sampleRate 를 이용해서 처리 및 저장하는 함수다.  
        // python 에서의 들여쓰기 구조가, 여기서는 {} 이렇게 표현됨 : 이 {}안이 함수 내부가 되는것.
{
    dsp::Gain gain;
        //dsp:: - 어디에 있는 클래스 인지
        //Gain : 설계도(Class). Gain.h 에 만들 설계도. Gain.h 에 gain 이라는 객체가 정의되어야 한다.
        //gain : 객체 이름(변수). Gain 이라는 설계도로 만든 gain 이라는 객체를 하나 만듦.
    gain.prepare (sampleRate);
        /* Gain 이라는 클래스 안에 이런 함수들이 들어있음. prepare 은 함수 _.prepare : prepare 함수 실행
        : Gain 클래스 안에 내가 만들어놓은 void prepare (Member function)
        => void 는 값을 반환하지는 않지만, 어떤 변수안에 어떤 값이 저장된 상태가 되도록 만들게 된다. (객체의 내부상태(state)만 바꿈)

        class Gain
        {
        public:

            void prepare(...);

            void setGainLinear(...);

            float processSample(...);

        };
        */
    gain.setGainLinear (linearMagnitude);

    std::vector<float> output (inputWave.size()); 
        // __.size : vector 클래스 안에 원래 정의되어 있는 멤버 함수 => 객체.멤버함수() 의 역할
        // size : inputWave 객체에게 원소 몇개 있는지 물어보는 함수
        // 따라서 그 개수만큼의 원소를 가진 새로운 vector 를 만드는 것 
    float peakAbsValue = 0.0f;
        // 이건 float 변수 하나 생성하고, 초기값이 0.0 인것 
        // 나중에 peakAbsValue = std::max(peakAbsValue, std::abs(processed)); 이렇게 현재까지 중에서의 가장 큰 절대값 저장하는 역할을 함

    for (size_t i = 0; i < inputWave.size(); ++i) 
        // 초기화; 조건; 반복후 1증가
        // size_t = 자료형(type) : 배열의 크기나 인덱스를 표현하기 위해 만든 자료형 (vector.size, string.size(), array.size()는 다 size_t 를 반환함)
    {
        float processed = gain.processSample (inputWave[i]);
            // 아마 내부에서는 return intput * gainLinear; 가 실행되고 있을듯 

        if (invert) // phase invert 처리
            processed = -processed;

        output[i] = processed;
        peakAbsValue = std::max (peakAbsValue, std::abs (processed));
    }

    const float dB = dsp::gainToDecibels (linearMagnitude);

    // 콘솔에 글자 출력하는 코드 std::cout = print()
    std::cout << std::fixed << std::setprecision (3); //고정소수점, 소수점 셋째 자리까지 출력
    std::cout << "[" << waveName << "]" //출력 시작 (<< : 계속 이어붙여라!) -> [waveName] 출력
                    << "magnitude=" << linearMagnitude
                    << ", invert=" << (invert ? "true" : "false") //invert 가 트루면 true 아니면 false 출력
                    << ", dB=" << dB
                    << ", peak=" << peakAbsValue;

    if (peakAbsValue > 1.0f)
        std::cout << " << 경고: 0dBFS(1.0)를 초과해서 wav 저장 시 클리핑 발생함";

    std::cout << "\n"; //줄바꿈

    const std::string invertTag = invert ? "_inv" : ""; //invert했으면 _inv 붙이고 아니면 없음
    const std::string filename = waveName + "_" + std::to_string(dB) + "dB" + invertTag + ".wav";
    dsp::writeMonoWav16 (filename, output, static_cast<uint32_t> (sampleRate));


}


// (4) main() <- 여기가 python 의 if __name__ = "__main__": 과 같은 파트
int main() 
{
    const double sampleRate = 48000.0;
    
    const auto sineWave = createSine (sampleRate, 200.0, 1.0);
    const auto noiseWave = createWhiteNoise (sampleRate, 1.0);
        //auto : 컴파일러가 자료형을 알아서 추론(infer)해라 
        // sine 은 std::vector<float> sineWave = .. 이렇게 만들었기 때문에 컴파일러가 자동으로 vector<float>으로 결정해줌
        // ex. 3 <- 처럼 float, double 인지 애매한 경우에는 안씀 auto 를 

        // 아래는 {크기, 위상반전여부} 를 쌍으로 정리한 것 
        struct GainCase { float magnitude; bool invert;};
            //float magnitude, bool invert를 하나로 묶어놓은 자료형이다.
        const std::vector<GainCase> gainCases = {
            {1.0f, false},
            {0.0f, false},
            {0.5f, false},
            {0.5f, true},
            {2.0f, false},
            {2.0f, true}, 
            // vector 안에 GainCase 를 여러개 넣어놓음
        };
        
        std::cout << "===Sine wave gain test===\n";
        for (const auto& c : gainCases) // == for c in gainCases: 와 같음!. range-based for loop
            applyGainAndSave (sineWave, "sine", c.magnitude, c.invert, sampleRate);
                //지금 여기에서의 auto 는 GainCase 자료형을 추론함
                // & : 복사하지 말고 원본을 그대로 사용 
                // const : 읽기 전용 (c.magnitude = 100; 이렇게 수정 못함)
                // const auto& c = const gainCase& c
                // 파이썬에서는 for c in gainCases 

                // applyGainAndSave 가 호출되는것!
                /* 아래와 같다.
                applyGainAndSave(
                                sineWave,
                                "sine",
                                1.0,
                                false,
                                sampleRate);
                */

        std::cout << "\n===White noise gain test ===/n";
        for (const auto& c : gainCases)
            applyGainAndSave (noiseWave, "noise", c.magnitude, c.invert, sampleRate);


        return 0;
        // main 함수는 int 를 반환해야한다. 꼭 정수를 하나 돌려줘야 함
        // 운영체제(OS)한테 반환 -> 0이 리턴되면 정상적으로 처리가 끝났다고 알아차림 (1이 리턴되면 뭔가 문제가 있었구나..!함)
        // 운영체제에게 정상적으로 끝났다고 알려주는것! 
}







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

! 참고로 int 는 정수 (샘플개수, 인덱스 처리등에 쓰임)
! char     // 거의 안 쓰지만 파일 처리 등에서 사용 (문자 한개)
*/

/* C++ 에서의 객체

    std::random_device rd;
    std::mt19937 engine (rd());
    std::uniform_real_distribution<float> distribution (-1.0f, 1.0f);
 
    for (int i = 0; i < numSamples; ++i)
        buffer[static_cast<size_t> (i)] = distribution (engine);
 
    return buffer;



    => 위 코드에서의 rd, rd(), distribution(engine) 
    : 함수인것 같지만 사실상 함수가 아니고 객체이다.

    ex. x.append(4) 는 리스트가 append 라는 기능을 가지고 있는것이다. 
    ex. rng = random.Random() <- 여기서 rng 도 함수가 아니다.
        => rng.randint(1,10) : 이렇게 사용할 수 있다.

    **함수는 내부에 기억하는 상태(state) 가 없음
    -> 그치만 함수가 아닌 객체여도 () 를 붙이면 이 객체가 이렇게 행동한다를 정의 할 수 는 있음

1) 객체 (Object) : 데이터와 그 데이터를 다루는 기능을 함께 가진것
2) 함수 (Function) : 입력을 받아 계산해서 결과를 돌려주는 코드
*/
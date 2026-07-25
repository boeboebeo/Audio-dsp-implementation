// Gain.h : Gain 알고리즘을 담음 (Header)

#pragma once    // 다른 main.cpp 에서 #include "Gain.h" 하면 
                // 컴파일러는 Gain.h 내용을 그대로 복붙함 -> 근데 두번 불러온다면 두개씩 복사되니까 그냥 이 헤더는 한번만 포함하라는 뜻! 
#include <algorithm>    // std::clamp 사용을 위함
#include <cmath>        // std::log10, std::pow 사용을 위함

/* namespace란?
: 이름들이 모여있는 공간(폴더)

Gain 이라는 클래스가 내가 만든것도 있고, JUCE 에도 존재한다면 
컴파일러는 어디의 Gain 인지 구분하지 못함
=> 그래서 namespace 를 사용하는것! 

    ex. namespace 가 dsp 라면 이 클래스의 이름은
        dsp::Gain

    ex. namespace 가 juse 라면
        juce::Gain 
        => 둘은 이름은 같지만 완전히 다른 경로를 가지고 있음

    ** std::vector 여기의 std 또한 namespace 

    ex.
    namespace mudmud
    {
        void hello()
        {
            std::cout << "Hello";
        }
    }
            => 이걸 사용할때는 mudmud::hello(); 가 됨 

*/ 

namespace dsp
{
    // dB <-> linear 변환 함수
    // 여기서는 JUCE 의 juce::Decibels 과 동일하게 처리하여 
    // 1) 음수 게인 : log10 -> nan, 2) gain=0 : -inf 로 처리함
    // 또한 0이하의 선형 게인은 무조건 floorDb(기본 -100dB)로 취급한다는 규칙을 강제함
    // -infinity 를 그대로 쓰면 골치아프므로, -100dB : 선형으로 약 0.00001배 하여 바닥으로 처리해 버림
    inline float gainToDecibels (float linearGain, float floorDb = -100.0f) noexcept
        //inline: 함수가 짧다면 굳이 호출을 하지 않고 그 자리에 이 함수 내용을 펼쳐 넣어버림
    {
        const float magnitude = std::abs (linearGain);
            //크기만 봄

        if (magnitude <= 0.0f)
            return floorDb; // linearGain 은 abs 처리를 했고, 
                            // log10(0)은 계산할 수 없으므로 바닥값 리턴(-100.0f)

        return std::max (floorDb, 20.0f * std::log10 (magnitude));
        // -100.0f 와 dB 계산한 것중에 큰것 출력. 
        // linearGain 이 0이면 출력되는것은 -100.0f를 반환
    }


    inline float decibelsToGain (float decibels, float floorDb = -100.0f) noexcept
    {
        // floorDb 보다 더 작은 dB 값이 들어오면 아예 0으로 처리. 완전한 무음은 0을 곱해야하는거니까

        if (decibels <= floorDb)
            return 0.0f;

        return std::pow(10.0f, decibels * 0.05f); // 0.05 = 1/20
        //다시 decibel -> linearGain 변환. 즉 10^(dB/20)
    }

    //======================================================================
    //Gain class 
    // JUCE 의 juce::dsp::Gain<float> 과 유사하게 짜여져 있는 코드임 
    // prepare() -> 처리 시작 전 1회 호출 (샘플레이트 등록)
    // setGainDecibels() / setGainLinear() -> 목표 게인 설정
    // processSample() -> 샘플 1개씩 처리 (JUCE 의 실시간 처리방식과 유사한 "1 sample씩" 구조)
    // reset() -> 내부 상태 초기화
    //
    // JUCE / 실시간 오디오는 "한 샘플씩", 또는 "작은 블럭 단위로" 처리하는 구조
    // Python 처럼 apply_gain(전체배열) -> 이런거는 실시간에서는 사용하지 않음

    class Gain //Gain 이라는 새로운 Class 를 만듦
    {
    public: //public : 밖에서 사용할 수 있는 부분 이 Class 밖에서도 
            // Gain g;
            // g.prepare(); <- 이렇게 접근해서 쓸수있다. 
            // private : 클래스 내부에서만 사용 가능
        Gain() = default;
            // 초기값으로 뭘 넣고 싶으면 직접 생성자를 만드는데 (ex. Delay 에서의 Buffer 크기 확보 등)
            // 이건 초기값으로 뭘 넣을일이 없음. Gain 은 버퍼도 없고, 초기화도 거의 없어서 이렇게 빈 생성자 만듦(컴파일러가 기본 생성자를 자동 생성하게 함)

        // 처리시작전에 한번 호출. 샘플레이트와, 게인이 바뀔때 얼마나 부드럽게 보간(ramp)할지 (ms단위)를 등록함
        // 스무딩(ramp)가 필요한 이유
        // : 게인을 0.5에서 갑자기 2.0으로 바꾸면 click 이 발생함 -> 서서히 목표값까지 여러샘플에 거쳐 다가가도록 만듦
        void prepare (double newSampleRate, double rampMilliseconds = 20.0) noexcept
        {
            sampleRate = newSampleRate; // 샘플레이트 등록
            rampMs = rampMilliseconds; //ramp 시간 등록
            reset(); // 내부 상태도 초기화 (위에서 등록한 설정값을 초기화하는 것이 아님) -> 아래의 reset() 확인! 
        }
        // 내부 상태 초기화 (현재 게인을 목표게인으로 즉시 맞추고, 스무딩 진행중인것도 리셋)

        // prepare() 안에서도 호출되고, 나중에 JUCE의 reset() 과 동일한 타이밍(재생 시작 시 등)에 불러주면 됨
        void reset() noexcept
        {
            currentGain = targetGain;
            rampSamplesRemaining = 0; // 이걸 초기화 한다는 뜻 
        }

        void setGainDecibels (float newTargetDb) noexcept
        {
            setGainLinear (decibelsToGain (newTargetDb));
        }

        void setGainLinear (float newTargetGain) noexcept
        {
            if (newTargetGain == targetGain)
                return; // 같은 값이면 다시 램프 시작할 이유 없음

            targetGain = newTargetGain; // 새롭게 적용된 TargetGain 이 새로운 목표게인으로 갱신됨

            // 몇 개의 샘플에 거쳐 목표값까지 도달할지 계산함
            // ex. sample rate : 48000Hz, ramp = 20ms 
            // -> 48000*0.02 : 960 samples 에 거쳐서 서서히 변함

            totalRampSamples = static_cast<int> (sampleRate * (rampMs / 1000.0));
            if (totalRampSamples < 1)
                totalRampSamples = 1;

            rampStep = (targetGain - currentGain) / static_cast<float> (totalRampSamples);
                //targetGain 에서 currentGain 을 뺀 값을 전체 RampSamples 수 만큼 나누면
                // 한 샘플이 변화할때의 한 단계가 나옴
                // increment per sample

            rampSamplesRemaining = totalRampSamples;
                // 다 변화할때까지 남은  샘플개수

            
        }

        // 샘플 1개를 받아서, 현재 게인을 곱한 값을 돌려줌
        // noexcept : 이 함수는 절대 예외를 던지지 않는다고 컴파일러에게 약속하는것
        // (실시간 오디오에서 예외처리는 예측 불가능한 지연을 만들 수 있어서
        // 실무에서는 오디오 처리 경로에 예외를 아예 안 쓰는 경우가 많다.)
        float processSample (float input) noexcept
        {
            if (rampSamplesRemaining > 0) // 램프동안 남은 샘플이 1개 이상이라면
            {
                currentGain += rampStep; // 타입(자료형)은 변수를 "처음 만들때만" 씀! 
                                         // currentGain 은 같은 클래스 안에(클래스 안에서 생성) 만들어져 있는것 이므로 member 변수 . 여기서도 사용가능
                --rampSamplesRemaining; //--: 1감소시키는 연산자(decrement operator)
                                        //rampSamplesRemaining 값이 하나 줄어듦
            }
            else // 남은 스텝이 없으면
            {
                currentGain = targetGain;
            }

            return input * currentGain;

        }

        float getCurrentGainLinear() const noexcept { return currentGain; }
        float getCurrentGainDecibels() const noexcept { return gainToDecibels (currentGain); }
            // 그냥 LinarGain 은 현재 적용되고 있는 currentGain 그대로 출력
            // Decibel 로 받으려면 gainToDecibles 에 currentGain 연산해서 출력
    
    private:
        double sampleRate = 44100.0;
        double rampMs = 20.0;

        float currentGain = 1.0f; // 지금 이 순간 곱해지고 있는 게인
        float targetGain = 1.0f; //최종적으로 도달해야 하는 게인

        float rampStep = 0.0f; // 초기화
        int totalRampSamples = 0; //초기화
        int rampSamplesRemaining = 0; //초기화

            
    };

    
}


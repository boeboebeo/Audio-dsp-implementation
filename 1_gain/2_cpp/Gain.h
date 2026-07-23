// Gain.h : Gain 알고리즘을 담음 (Header)

#pragma once
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
    {
        const float magnitude = std::abs (linearGain);
            //크기만 봄

        if (magnitude <= 0.0f)
            return floorDb; // 0보다 작으면 부동소수점 오차로 음수가 될수있으니 바닥값 리턴(-100.0f)

        return std::max (floorDb, 20.0f * std::log10 (magnitude));
        // -100.0f 와 dB 계산한 것중에 큰것 출력. linearGain 이 0이면 출력되는것도 0
    }


    inline float decibelsToGain (float decibels, float floorDb = -100.0f) noexcept
    {
        // floorDb 보다 더 작은 dB 값이 들어오면 아예 0으로 처리. 완전한 무음은 0을 곱해야하는거니까

        if (decibels <= floorDb)
            return 0.0f;

        return std::pow(10.0f, decibels * 0.05f); // 0.05 = 1/20
        //다시 decibel -> linearGain 변환. 즉 10^(dB/20)
    }
}


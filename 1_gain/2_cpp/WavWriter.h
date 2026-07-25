// WaveWriter.h : wav 저장하는 파일

#pragma once
#include <string>
#include <vector>
#include <fstream>
#include <cstdint>
#include <algorithm>
#include <iostream>

// WAV 는 파일 앞부분에 44바이트 까지 고정된 "헤더"가 붙고, 그 뒤에 실제 샘플 데이터가 오는 포맷 

namespace dsp
{
    // 16bit PCM mono WAV 파일 -> 실행하고 나서 값을 반환하지 않음
    // samples 는 -1.0 ~ +1.0 범위의 float 벡터로 가정 (JUCE 관례와 동일)
    inline void writeMonoWav16 (const std::string& filename,
                                const std::vector<float>& samples, // float 샘플 받아서 16-bit Mono WAV 파일로 저장하는 함수
                                uint32_t sampleRate)
        // inline: 함수 호출하는 대신 그 함수 코드를 그 자리에 펼쳐버리기 (함수가 짧을 경우)
        // std::string& filename : 변수이름 filename 의 문자열 참조하겠다(&)는 것.
            // => 통째로 복사해서 가져오는대신 원래 문자열 그대로 참조하여 사용하겠다!
        // std::vector<float>& sample : samples 의 내용 그대로 참조 + 수정하지 않겠다
            // => 10초짜리 48kHz 오디오면 480,000samples 만큼의 샘플이 있는데, 그걸 매번 복사하면 쓸데없이 메모리와 CPU 를 사용함
        // uint : unsigned integer. 음수가 없는 정수 (정수형 자료형) => 음수가 아닌 32-bit 정수
    {
        //std::ofstream: C++표준 파일 출력 스트림. python 의 (file, "wb")와 비슷한 역할
        //std::ios::binary: 텍스트가 아니라 바이너리 그대로 쓰겠다는 뜻 (WAV)는 텍스트 포맷이 아님
        std::ofstream file (filename, std::ios::binary);
            //ofstrea : 파일 출력하는 통로
            // file 이라는 객체 하나 만들어서 오른쪽 (filename, std::ios::binary) 전달함
            // 어떤 파일을 열건지(filename), 어떤 모드로 열건지(std::ios::binary) -> WAV는 텍스트 파일이 아니라 바이너리 파일
        if (! file.is_open()) // 파일 제대로 열렸니? 물어보는 함수
            // ! : not => 파일이 제대로 열리지 않았다면 아래 {} 안 내용 실행 
        {
            std::cerr << "파일을 열 수 없습니다: " << filename << "\n";
                //cerr == cout 과 거의 유사한데 에러/경고 메시지 출력용
            return;
        }
    }
}

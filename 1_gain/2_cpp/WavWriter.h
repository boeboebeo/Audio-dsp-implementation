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
            return; //그리고 void 함수니까 이거 함수 실행 끝내고 나가라
        }

        // 각각 uint32(4bytes), 16(2bytes)에 따라서 메모리에서 차지하는 공간이 달라짐 
        // 그리고 WAV 헤더는 각 항목마다 몇 byte를 사용해야 하는지 이미 규격으로 정해져 있음 -> 아래와 같이
        const uint32_t numSamples   = static_cast<uint32_t> (samples.size()); //전체 샘플 개수
            // uint32_t : C++에서 사용하는 정수 자료형 (음수표현하지 않는, 32bit(4 byte), type)
        const uint16_t numChannels  = 1; // 채널 개수 (mono WAV , stereo면 2)
        const uint16_t bitsPerSample = 16;
        const uint32_t byteRate     = sampleRate * numChannels * (bitsPerSample / 8); // 1초동안 필요한 byte 수
        const uint16_t blockAlign   = numChannels * (bitsPerSample / 8); // 한 샘플을 저장하는데 필요한 바이트 수 
        const uint32_t dataSize     = numSamples * (bitsPerSample / 8); // WAV 의 실제오디오 데이터 전체가 차지하는 byte 수
        const uint32_t chunkSize    = 36 + dataSize; // 전체파일 크기 - 8byte (파일 전체크기에서 앞쪽 8 byte 를 제외한 크기)
        // 청크사이즈 계산시에는 RIFF 와 chunksize 8bytes 는 빠짐
            // WAVE 파일 전체 크기 : RIFF Header + fmt chunk(36) + data chunk(실제 오디오 데이터)
            // RIFF 8 bytes: Resource Interchange File Format
            // WAVE 
            // 실제로 ASCII 로 해석하면 R I F F 가 각각 52, 49, 46, 46 이렇게 들어가 있음 + WAVE 식별자도 들어감
            // "RIFF" (4 bytes) + chunksize (4 bytes) + "WAVE"(4 bytes)<-식별자
            // "RIFF" + chunksize 의 총 8byte 가 빠지게 되는것 .
            // 36byte + 실제 오디오 데이터 크기



        
        // WAV 포맷 명세에 정해진 정확한 순서/바이트 크기 (임의로 바꾸면 안됨)
        // C++에서 파일에 원시바이트를 쓸때는 write((const char*)&value, sizeof(value)) 패턴을 사용
        auto writeChars = [&file] (const char* data, size_t count) {file.write (data, static_cast<std::streamsize> (count));};
            // lambda 방식으로 writeChars라는 함수 하나 만든것
            // [&file] : 위에서 만든 ofstream file 객체. 위 함수 안에서 file 객체를 수정없이 그대로 사용하겠다(&)
        auto writeU32 = [&file] (uint32_t v) { file.write (reinterpret_cast<const char*> (&v), sizeof (v));};
            // sizeof(v) : v 가 메모리에서 몇 byte 를 차지하는지 알려줌
        auto writeU16 = [&file] (uint16_t v) { file.write (reinterpret_cast<const char*>(&v), sizeof(v));};

        /* WAV 파일 구조
        => 아래에서 그대로 쓰이고 있는 HEADER
        ┌─────────────────────────────┐
        │ RIFF        4 bytes         │
        │ chunkSize   4 bytes         │
        │ WAVE        4 bytes         │ 
        ├─────────────────────────────┤ 
        │ fmt         4 bytes         │
        │ fmt size    4 bytes         │
        │ audio fmt   2 bytes         │
        │ channels    2 bytes         │
        │ sampleRate  4 bytes         │
        │ byteRate    4 bytes         │
        │ blockAlign  2 bytes         │
        │ bitDepth    2 bytes         │
        ├─────────────────────────────┤
        │ data        4 bytes         │
        │ dataSize    4 bytes         │
        ├─────────────────────────────┤
        │ 실제 PCM 샘플 데이터            │
        └─────────────────────────────┘
        */

        // WAV header
        // - - - - RIFF 헤더 - - - - 
        writeChars ("RIFF", 4);
        writeU32 (chunkSize); // chunkSize를 4바이트 정수로 기록함
        writeChars ("WAVE", 4); //얘도 4 byte

        // - - - - fmt 서브청크 (오디오 포맷 정보) - - - -
        writeChars ("fmt ", 4); // "fmt ": 이렇게 마지막에 띄어쓰기 까지 해야 4 byte
        writeU32 (16); // fmt 청크 크기 (PCM 은 항상 16) -> 16을 4 byte 로 기록함
        writeU16 (1); // 오디오 포맷 코드 : 1 = PCM (비압축)이라는 뜻. 2byte로 저장
        writeU16 (numChannels); // 2byte로 저장
        writeU32 (sampleRate); // 4byte로 저장
        writeU32 (byteRate); //4
        writeU16 (blockAlign); //2byte로 저장
        writeU16 (bitsPerSample); 
            //한 샘플을 16 bit로 저장한다 라는 정보를 WAV파일에 기록
            //WAV 파일을 읽는 프로그램이 이 정보를 보고, 데이터 영역에서 몇 바이트씩 끊어서 하나의 샘플로 해석해야 하는지를 결정함

        // - - - - data 서브청크 (실제 샘플) - - - - 실제 오디오 데이터
        writeChars ("data", 4); 
        writeU32 (dataSize); // 실제 오디오 데이터가 총 몇 byte인지

        // float(-1 ~ +1) 샘플을 16 bit 정수 (-32768 ~ +32768)로 변환해서 저장함
        // 이 과정에서 실제로 클리핑이 일어남. std::clamp 로 범위를 강제로 제한하기 때문
        for (float sample : samples) // for sample in samples
        {
            const float clamped = std::clamp (sample, -1.0f, 1.0f); 
                //-1.0 ~ +1.0 범위의 float 샘플을 16bit PCM 정수로 바꾼 다음 
                // 그 정수의 실제 바이트를 WAV 파일에 하나씩 기록하는 코드
                // std::clamp : 값을 특정범위 안에 강제로 넣는것. -1.5 -> -1.0 으로
                // 따라서 원래의 -1.5라는 정보가 사라짐

            const int16_t intSample = static_cast<int16_t> (clamped * 32767.0f);
                // 여기서 float 을 16-bit PCM 정수로 바꾸는것이 일어남
                // float 은 -1.0 ~ 1.- 사이니까 거기에 * 32767 하면 int 16이 됨 (약 -32767 ~ +32767)
                // int16_t를 써서 샘플 하나를 2bytes 로 표현함
            file.write (reinterpret_cast<const char*> (&intSample), sizeof (intSample));
                // 방금만든 int16_t 숫자를 실제 바이너리 바이트로 파일에 써라
                // 이제 intSample 이 위에서 16384가 되었다면, 그 만큼의 사이즈인 2bytes(sizoof)로 표현
                // reinterpret_cast<const char*> : int16_t 의 메모리를 그냥 바이트 데이터라고 보고 읽어라

        }

        file.close(); //파일쓰기를 끝내고 파일을 닫는다.
    }
}


/* WAV
: Input wave 를 받아서

 -> std::vector<float> 처리하고 ex. [0.0, 0.026, 0.052, ...]

 -> float 값을 16-bit PCM(비압축) 정수로 변환

 -> 바이너리 데이터로 저장 (PCM 정수값으로 변환하여 저장)

 -> 따라서 16384 라는 숫자가 실제 파일에서는 00000000 01000000 이렇게 두 바이트가 들어간다. 

    **컴퓨터에서는 보통 8bit = 1 byte 단위로 데이터를 다룸

    ex. 352 
        = 100 * 3 + 10 * 5 + 1 * 2 = 352 (각 자리수에서 10의 거듭제곱 배정)

    ex. 2¹⁵    2¹⁴  2¹³  2¹²  2¹¹  2¹⁰  2⁹  2⁸
        ↓      ↓    ↓    ↓    ↓    ↓    ↓    ↓
        32768 16384 8192 4096 2048 1024 512 256

        2⁷    2⁶   2⁵   2⁴    2³   2²   2¹   2⁰
        ↓     ↓     ↓    ↓    ↓    ↓    ↓    ↓
        128   64   32   16    8    4    2    1

        => 16384를 표현한다면 그 자리 하나만 1이면 됨
        01000000 00000000

        => 근데 실제 WAV 의 일반적인 little- endian 저장순서에 따라서 실제 바이트가
        : 00000000 01000000 으로 바뀜

*/
import openai

# API 키 설정
openai.api_key = "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"

# GPT 모델을 사용한 텍스트 생성
response = openai.ChatCompletion.create(
    model="gpt-4o-mini",  # 사용할 모델을 지정합니다.
    messages=[
        {"role": "user", "content":
            "ㅎㅇㅎㅇ"
        }
    ],
    max_tokens=1000
)

# 생성된 텍스트 출력
print(response['choices'][0]['message']['content'].strip())  # 'message'로 수정

# "내가 지금 도시지역을 입력하면 해당 도시의 날씨를 확인해서 "
#             "날씨 키워드를 Clear: 맑음, Clouds: 구름, Rain: 비, "
#             "Drizzle: 가벼운 비, Thunderstorm: 천둥번개, Snow: 눈, "
#             "Mist: 안개, Fog: 짙은 안개로 나눴어. 이후 데이터베이스에 "
#             "영화 정보가 있는데 그중 데이터 중에 weather 필드가 있고 "
#             "'weather_condition'과 일치하면 해당 영화들이 나오도록 하고 있어. "
#             "그런데 영화를 추천하는 기준이 날씨만으로 되어 있는데 나는 이것뿐만 아니라 "
#             "user가 가지고 있는 선호도 중 장르도 고려해서 선호하는 장르까지 있으면 추천하는 느낌으로 해보고 싶어."
# 가정: closed_school_df, closed_house_df, memorial_park_df는 각각 폐교, 폐가, 추모공원 데이터셋을 담고 있는 DataFrame 객체
# mortality_df는 사망률 데이터셋을 담고 있는 DataFrame 객체

import pandas as pd

# CSV 파일에서 데이터 불러오기
closed_school_df =pd.read_csv('/Users/yuming/ghost_data/closed_school.csv',  encoding='cp949')
closed_house_df = pd.read_csv('/Users/yuming/ghost_data/closed_house.csv',  encoding='cp949')
memorial_park_df = pd.read_csv('/Users/yuming/ghost_data/memorial_park.csv',  encoding='cp949')
mortality_df = pd.read_csv('/Users/yuming/ghost_data/mortality.csv',  encoding='cp949')

# 각 데이터 셋에 카운트 열 추가
closed_school_df['school_count'] = 1
closed_house_df['house_count'] = 1
memorial_park_df['park_count'] = 1

# 'province', 'city', 'district'를 기준으로 각각 그룹화 후 카운트 계산
school_grouped = closed_school_df.groupby(['province', 'city', 'district'])['school_count'].count().reset_index()
house_grouped = closed_house_df.groupby(['province', 'city', 'district'])['house_count'].count().reset_index()
park_grouped = memorial_park_df.groupby(['province', 'city', 'district'])['park_count'].count().reset_index()

# 세 개의 그룹화된 데이터 셋 병합
merged_1 = pd.merge(school_grouped , house_grouped , on=['province','city','district'], how='outer')
merged_total = pd.merge(merged_1 , park_grouped , on=['province','city','district'], how='outer')

# NaN 값 처리 (NaN은 해당 지역에서 관련 시설이 없음을 의미)
merged_total.fillna(0, inplace=True)

# 마지막으로 사망률 데이터 셋 병합 ('how' 파라미터를 사용하여 필요한 방식의 조인 수행)
final_merged_data= pd.merge(merged_total,mortality_df,on='province',how='inner')

# province를 기준으로 그룹화 후 die 열의 평균 계산
mortality_avg = mortality_df.groupby('province')['die'].mean().reset_index()

# 마지막으로 평균 사망률 데이터 셋 병합
final_merged_data= pd.merge(merged_total,mortality_avg,on='province',how='inner')

# 사용자로부터 지역 정보 입력 받기
province = input("도를 입력하세요: ")
city = input("시를 입력하세요: ")
district = input("동을 입력하세요: ")

def calculate_probability(df, province, city, district):
    # 해당 지역의 데이터 행 찾기
    row = df[(df['province'] == province) & (df['city'] == city) & (df['district'] == district)]
    
    if len(row) == 0:
        return "해당 위치에 대한 데이터가 없습니다."
    
    # 폐교, 폐가, 추모공원 개수 및 사망률 값을 가져옴
    school_count = row['school_count'].values[0]
    house_count = row['house_count'].values[0]
    park_count = row['park_count'].values[0]
    mortality_rate = row['die'].values[0]  # 'die' 열이 사망률을 나타낸다고 가정
    
    # 가중치 적용: 사망률 4점, 폐교/폐가/추모공원 각각 2점
    weighted_total = mortality_rate * 4 + school_count * 2 + house_count * 2 + park_count * 2

    # 정규화 및 퍼센트 변환: 전체 점수를 가중치 합계로 나눈 후 x100
    probability_percent = (weighted_total / (4+2+2+2)) * 100
    
    return probability_percent

probability_percent= calculate_probability(final_merged_data, province, city, district)
print(f"귀신이 나타날 확률은 {probability_percent}입니다.")
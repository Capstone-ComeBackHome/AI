# AI
세종대학교 캡스톤디자인 수업 **컴백홈**팀의 **AI 진단 챗봇 어플 Apzima**의 AI 깃허브입니다.  
세종대학교 창의설계경진대회 **은상** 수상


## 1. 프로세스
  ![process_ver3](https://user-images.githubusercontent.com/59015764/177354681-c4976adc-3215-4360-9139-51e2ed0ec63b.png)
 ### 1) Two Stage Process
 * 배경
   * 환자 진료 시 ‘증상’, ‘증상 시작 시점’ 등 공통적인 질문 소재도 있지만, 환자의 증상에 따라 추가적인 질문이나 하지 않는 질문 등이 존재 
    * 따라서 환자의 증상에 따라 챗봇이 환자에게 적절한 질문을 필요하다고 판단
    * 그에 따라 전체 프로세스를 증상 분류와 질병 분류 두 가지 단계로 나누어 설계
 * 결론
   * 공통질문으로 주요 증상, 증상 시작 시점에 대한 답변을 받고 그를 이용하여 환자의 증상 라벨 추론
   * 추론 결과를  기반으로 클래스 별로 미리 준비된 질문 리스트를 프론트에 전달 
   * 해당 질문들에 대한 환자의 답변을 이용해 진단 모델에서 최종 질병을 추론   
 ### 2) Filter 
   * 배경 
     * ‘월경 과다’, ‘전립선염’ 등 여성 또는 남성에게만 나타나는 증상, 질병이 존재  
   * 결론
      * 배포 시에는 추론 결과를 성별에 따라 필터링하는 과정을 추가  
      
## 2. 데이터
Back Translation Augmentation
  * 배경 
    * 샘플 수가 적고 Class Imblanace가 심함
  * 해결
    * 샘플수가 5개 이하인 클래스에 한해 Back Translation Augmentation을 진행
    * Google Cloud Trnaslation API를 이용해 영어, 중국어, 일본어, 독일어, 스페인어를 거쳐 재번역
    ![image](https://user-images.githubusercontent.com/59015764/177358783-af059e41-b1ed-47f4-8a14-9348c123cf05.png)
    ###### [이미지 출처] https://amitness.com/back-translation/


## 3. 증상 모델
![level2_ver2](https://user-images.githubusercontent.com/59015764/177360558-8ff4c4d7-dbf0-4bd1-b23b-34ccb6cb9aea.png)
* 환자의 증상에 따라 적절한 질문을 하기 위해 환자가 어떤 증상을 호소하고 있는지 분류
* Feature : 주요 증상, 증상 시작 시점, 나이, 성별
* 주요 증상과 증상 시작 시점의 경우 한두문장의 짧은 문장 이므로 간단한 수치화와 분류 모델을 이용해도 충분한 성능을 낼 수 있다고 판단
* 전처리
  * konlpy의 Okt를 사용하여 토큰화
  * ‘이’, ‘가’, ‘을’, ‘를’ 등의 불용어 제거
  * 텍스트를 수치화하기 위하여 통계 기반 가중치를 추출할 수 있는 sklearn의 TF-IDF vectorizer를 사용
* 학습
  * 과적합 방지를 위해 얕은 신경망 사용

## 4. 진단 모델
![diagnosis](https://user-images.githubusercontent.com/59015764/177361980-2c45cd44-3de4-4a17-adb3-8854da0eb791.png)
* 환자의 모든 답변을 이용하여 최종 질병명을 예측
* 데이터 전처리
  * Back Translation Augmentation
* 학습
  * 데이터수가 충분하지 않음을 고려헤 전이학습 방법을 사용
  * 다양한 BERT모델로 실험 후 가장 좋은 성능의 KoBERT를 채택

## 5. 배포
* AWS EC2와 Flask를 이용하여 배포 
* [API 문서](https://documenter.getpostman.com/view/19596204/UVyxQDzM)

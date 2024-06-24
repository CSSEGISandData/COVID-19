# 존스홉킨스 대학교 시스템 과학 및 엔지니어링 센터(CSSE)에 의한 COVID-19 데이터 저장소


존스홉킨스대 시스템과학공학센터(JHU CSSE)가 운영하는 2019년 소설 코로나바이러스 비주얼 대시보드의 데이터 저장소다. 또한 ESRI Living Atlas 팀과 존스 홉킨스 대학 응용 물리학 연구소(JHU APL)의 지원을 받는다.


<br>

<b>Visual Dashboard (데스크톱):</b><br>
https://www.arcgis.com/apps/opsdashboard/index.html#/bda7594740fd40299423467b48e9ecf6
<br><br>
<b>Visual Dashboard (모바일):</b><br>
http://www.arcgis.com/apps/opsdashboard/index.html#/85320e2ea5424dfaaa75ae62e5c06e61
<br><br>
<b>Lancet 문서:</b><br>
[실시간으로 COVID-19를 추적할 수 있는 대화형 웹 기반 대시보드](https://doi.org/10.1016/S1473-3099(20)30120-1)
<br><br>
<b>존스 홉킨스 대학 시스템 과학 및 엔지니어링 센터(JHU CSE: JHUniversity Center for Systems Science and Engineering, JHU CSE:</b><br>
https://systems.jhu.edu/
<br><br>
<b>데이터 원본:</b><br>
- 집계된 데이터 원본:
  - 세계보건기구 (WHO): https://www.who.int/
  - 유럽 질병 예방 및 통제 센터 (ECDC): https://www.ecdc.europa.eu/en/geographical-distribution-2019-ncov-cases 
  - DXY.cn. 폐렴. 2020. http://3g.dxy.cn/newh5/view/pneumonia
  - US CDC: https://www.cdc.gov/coronavirus/2019-ncov/index.html
  - BNO 뉴스: https://bnonews.com/index.php/2020/02/the-latest-coronavirus-cases/
  - WorldoMeters: https://www.worldometers.info/coronavirus/  
  - 1Point3Arces: https://coronavirus.1point3acres.com/en  
  - COVID 추적 프로젝트: https://covidtracking.com/data. (미국 테스트 및 입원 데이터. 우리는 각 주에 보고된 입원 번호에 대해 "현재"와 "누적" 입원 치료의 최대 보고 값을 사용한다.)

- 주(Admin1) 또는 행정구역/도시(Admin2) 수준의 미국 데이터 소스:  
  - 워싱턴 주 보건부: https://www.doh.wa.gov/emergencies/coronavirus
  - 메릴랜드 보건부: https://coronavirus.maryland.gov/
  - 뉴욕 주 보건부: https://health.data.ny.gov/Health/New-York-State-Statewide-COVID-19-Testing/xdss-u53e/data
  - NYC 보건 정신 위생부: https://www1.nyc.gov/site/doh/covid/covid-19-data.page 및 https://github.com/nychealth/coronavirus-data
  - 플로리다 보건부 대시보드: https://services1.arcgis.com/CY1LXxl9zlJeBuRZ/arcgis/rest/services/Florida_COVID19_Cases/FeatureServer/0
    및 https://fdoh.maps.arcgis.com/apps/opsdashboard/index.html#/8d0de33f260d444c852a615dc7837c86
  - 콜로라도: https://covid19.colorado.gov/covid-19-data
  - 버지니아: https://www.vdh.virginia.gov/coronavirus/
  - 북마리아나 제도: https://chcc.gov.mp/coronavirusinformation.php#gsc.tab=0

- 국가/지역(Admin0) 또는 주/도(Admin1) 수준의 미국 이외의 데이터 소스:
  - 중화인민공화국 국가보건위원회(NHC):
    http://www.nhc.gov.cn/xcs/yqtb/list_gzbd.shtml
  - 중국 CDC (CCDC): http://weekly.chinacdc.cn/news/TrackingtheEpidemic.htm
  - 홍콩 보건부: https://www.chp.gov.hk/en/features/102465.html
  - 마카오 정부: https://www.ssm.gov.mo/portal/
  - 대만 CDC: https://sites.google.com/cdc.gov.tw/2019ncov/taiwan?authuser=0
  - 캐나다 정부: https://www.canada.ca/en/public-health/services/diseases/coronavirus.html
  - 호주 정부 보건부: https://www.health.gov.au/news/coronavirus-update-at-a-glance
  - COVID Live (호주): https://www.covidlive.com.au/
  - 싱가포르 보건부 (MOH): https://www.moh.gov.sg/covid-19
  - 이탈리아 보건부: http://www.salute.gov.it/nuovocoronavirus
  - Dati COVID-19 이탈리아 (이탈리아): https://github.com/pcm-dpc/COVID-19/tree/master/dati-regioni
  - 프랑스 정부: https://dashboard.covid19.data.gouv.fr/ 및 https://github.com/opencovid19-fr/data/blob/master/dist/chiffres-cles.json
  - OpenCOVID19 프랑스: https://github.com/opencovid19-fr
  - 팔레스타인 (West Bank and Gaza): https://corona.ps/details
  - 이스라엘: https://govextra.gov.il/ministry-of-health/corona/corona-virus/
  - 코소보 공화국 보건부: https://kosova.health/ 및 https://covidks.s3.amazonaws.com/data.json
  - 베를리너 모겐포스트 (독일): https://interaktiv.morgenpost.de/corona-virus-karte-infektionen-deutschland-weltweit/
  - rtve (스페인): https://www.rtve.es/noticias/20200514/mapa-del-coronavirus-espana/2004681.shtml
  - 세르비아 보건부: https://covid19.rs/homepage-english/ 
  - 칠레: https://www.minsal.cl/nuevo-coronavirus-2019-ncov/casos-confirmados-en-chile-covid-19/
  - 브라질 보건부: https://covid.saude.gov.br/
  - 브라질: https://github.com/wcota/covid19br. 설명된 데이터 [DOI: 10.1590/SciELOPreprints.362](https://doi.org/10.1590/SciELOPreprints.362)
  - 고베도 디에보르:https://covid19.sinave.gob.mx/
  - 일본 COVID-19 코로나바이러스 추적기: https://covid19japan.com/#all-prefectures
  - 페루의 COVID-19 -  페루 국립 경찰 (PNP) - 정보국 (DIRIN): https://www.arcgis.com/apps/opsdashboard/index.html#/f90a7a87af2548699d6e7bb72f5547c2
  - 콜롬비아: https://antioquia2020-23.maps.arcgis.com/apps/opsdashboard/index.html#/a9194733a8334e27b0eebd7c8f67bd84 및 [국립 보건원](https://www.ins.gov.co/Paginas/Inicio.aspx)
  - 러시아: https://xn--80aesfpebagmfblc0a.xn--p1ai/information/
  - 우크라인: https://covid19.rnbo.gov.ua/
  - 스웨덴 보건청: https://experience.arcgis.com/experience/09f821667ce64bf7be6f9f87457ed9aa
  - 인도 보건 가족 복지부: https://www.mohfw.gov.in/
  - 파키스탄 정부: http://covid.gov.pk/stats/pakistan
  - 영국 정부: https://coronavirus.data.gov.uk/#category=nations&map=rate
  - 스코틀랜드 정부: https://www.gov.scot/publications/coronavirus-covid-19-trends-in-daily-data/

<br>
<b>비주얼 대시보드를 위한 추가적인 정보:</b><br>
https://systems.jhu.edu/research/public-health/ncov/
<br><br>

<b>연락할 수 있는 수단: </b><br>
* Email: jhusystems@gmail.com
<br><br>

<b>사용하는 방법:</b><br>

1. 본 웹 사이트와 본 문서의 내용(모든 데이터, 지도 및 분석)("Website"), 저작권 2020 존스 홉킨스 대학교("Website"), 저작권 2020, 모든 권리 보유는 비영리 공중 보건, 교육 및 학술 연구 목적으로만 제공된다. 이 웹사이트에 의지하여 의사의 조언이나 지도를 받아서는 안 된다.  
2. 상업적 당사자 및/또는 상업상 웹사이트의 사용은 엄격히 금지된다. 웹사이트의 재분배 또는 웹사이트의 기초가 되는 집계된 데이터 세트의 재배포는 엄격히 금지된다.   
3. 웹사이트에 접속할 때, 웹사이트를 존스 홉킨스 대학교의 시스템 과학 엔지니어링 센터(CSSE)에 의한 COVID-19 대시보드 또는 존스 홉킨스 대학교의 시스템 과학 엔지니어링 센터(CSSE)에 의한 COVID-19 데이터 저장소로 간주한다.
4. 웹사이트는 항상 동의하지 않는 여러 출처의 공개적으로 이용할 수 있는 데이터에 의존한다. 존스 홉킨스 대학은 이에 의해 정확성, 사용 적합성, 신뢰성, 완전성 및 제3자 권리의 비침해를 포함한 웹사이트에 관한 모든 진술과 보증을 부인한다. 
5. 존스 홉킨스의 이름, 로고, 상표 및/또는 트레이드 드레스를 사실적으로 부정확한 방법이나 마케팅, 홍보 또는 상업적 목적으로 사용하는 것은 엄격히 금지된다.
6. 이러한 약관은 변경될 수 있다. 당신이 웹사이트를 사용하는 것은 본 약관 및 향후 변경사항을 수용하는 것으로 구성된다.

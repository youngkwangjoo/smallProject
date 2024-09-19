# smallProject
그냥 심심해서해보는 심심한 프로젝트

day = 07:00 ~ 15:00
evening = 14:30 ~ 22:30 
night = 22:00 ~ 07:30

규칙 
1. night 뒤에는 off off가 있어야한다.
2. 한사람이 연속되는 night는 최대 3번만 가능하다
3. 총 off수는 공휴일과 주말 갯수와 같다.
4. 매일 근무가 가능한 최대날은 5일이다.
5. evening다음에 day는 올수 없지만 day다음에는 evening이 올 수 있다.
6. 주말에 day, evening, night는 모두 2명씩 근무한다.
7. 평일에는 day 3명, evening 3명, night 2명이 근무한다.
8. 연차가 있는 인원은 해당 날짜에 근무 할 수 없다.
9. 입력된 사수와 부사수가 있고, 사수는 사수와 함께 근무할 수 있지만 부사수는 반드시 사수와 함께 근무해야한다.
10. evening 다음 night을 할수는 없다.

아무래도 로직을 추가해야할거같다. 간호사 수가 계속 부족하다는 오류가 발생하는데, 각 간호사별 최소 근무일수를 정해놔도 오류가 발생한다. 
1. 모든 간호사는 한달의 평일 갯수만큼 근무를 들어가야한다(근무일수를 입력)
2. night 근무 뒤에는 반드시 두타임 off,off가 필요하다.
3. 총 off 날은 공휴일과 주말 갯수와 같다. 
4. 연속해서 근무가 가능한 날은 최대 5일이다. 
5. evening 근무 다음에는 day 근무를 할 수 없다. 
6. day 근무 다음에는 Evening 근무가 올 수 있다. 
7. 주말 day, evening, night 근무는 2명이 들어간다. 
8. 평일에는 day 3명, evening 3명, night 2명이 근무한다.
9. 연차가 있는 인원은 해당 날짜에 근무할 수 없다. 
10. 입력된 사수와 부사수가 있고, 사수는 사수와 함께 근무할 수 있지만 부사수는 반드시 사수와 함께 근무해야한다.
11. evening 다음에 night 근무를 할 수 없다. 
12. 한달에 주말, 공휴일을 제외한 날짜 만큼 근무를 들어가야한다. (대략 20번정도)
13. 
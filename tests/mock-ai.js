// 테스트 전용 가짜 AI. claude.ai 밖에서는 window.claude가 없어서 진짜 AI가 안 돌기 때문에,
// 각 계층 프롬프트를 알아보고 미리 정해둔 답을 돌려준다. 게시용 teach-me.html에는 넣지 않는다.
window.claude = { use: function (name) {
  if (name !== 'sample') return Promise.resolve(null);
  var line = '알겠어요 선배! 근데 헌병 경찰이 바뀌었으면 이제 경찰이 줄어든 거예요?';
  var f = function (p, o) {
    if (o && o.onText) o.onText({ text: line, delta: line });
    return Promise.resolve({ text: line, truncated: false, modelTierApplied: 'quick' });
  };
  f.json = function (p) {
    (window.__prompts = window.__prompts || []).push({kind: p.slice(0, 60), len: p.length, text: p});
    // 예시 자료가 아닌 긴 자료(쪽 단위 테스트): 받은 원문 묶음에서 구간 시작 문장을 뽑아 흉내 낸다
    if (p.indexOf('자료 분석 계층') >= 0 && p.indexOf('무단 통치') < 0) {
      var body = p.split('<자료>\n')[1].split('\n</자료>')[0];
      var lines = body.split('\n').filter(function (l) { return l.trim().length > 20; });
      var a = lines[0], b = lines[Math.floor(lines.length / 2)];
      return Promise.resolve({
        title: '긴 자료 테스트', recommended_mode: 'flow', recommend_reason: '테스트',
        sections: [{ id: 's1', title: a.slice(0, 12), start: a.slice(0, 16) }, { id: 's2', title: b.slice(0, 12), start: b.slice(0, 16) }],
        goals: [{ id: 'g1', section: 's1', text: a.slice(0, 20) + '을 설명할 수 있다' }, { id: 'g2', section: 's2', text: b.slice(0, 20) + '을 설명할 수 있다' }],
        exam: [{ id: 'q1', section: 's1', goal: 'g1', kind: 'flow', question: a.slice(0, 20) + '?', answer: a.slice(0, 40), key_points: [a.slice(0, 10)], detail_points: [] },
               { id: 'q2', section: 's2', goal: 'g2', kind: 'flow', question: b.slice(0, 20) + '?', answer: b.slice(0, 40), key_points: [b.slice(0, 10)], detail_points: [] }]
      });
    }
    if (p.indexOf('자료 분석 계층') >= 0) return Promise.resolve({
      title: '일제의 식민 통치 방식 변화', recommended_mode: 'flow',
      recommend_reason: '통치 방식이 왜 바뀌었는지 흐름이 중요해서 흐름 이해를 추천해요.',
      sections: [
        { id: 's1', title: '1910년대 무단 통치', start: '1. 1910년대 무단 통치' },
        { id: 's2', title: '1920년대 문화 통치', start: '2. 1920년대 문화 통치' }],
      goals: [
        { id: 'g1', section: 's1', text: '무단 통치의 특징을 설명할 수 있다' },
        { id: 'g2', section: 's2', text: '문화 통치의 기만성을 설명할 수 있다' }],
      exam: [
        { id: 'q1', section: 's1', goal: 'g1', kind: 'flow', question: '무단 통치의 특징은?', answer: '헌병 경찰제로 강압적으로 지배했다.', key_points: ['헌병 경찰제'], detail_points: [] },
        { id: 'q2', section: 's2', goal: 'g2', kind: 'flow', question: '문화 통치가 기만적인 이유는?', answer: '보통 경찰제로 바꿨지만 경찰 수는 늘었다.', key_points: ['경찰 수 증가'], detail_points: [] }]
    });
    if (p.indexOf('이해 상태 추적기') >= 0) return Promise.resolve({
      goals: [{ id: 'g1', level: 2, note: '헌병 경찰제 설명함' }, { id: 'g2', level: 1, note: '언급만' }],
      misconception_updates: [],
      directive: { kind: 'misconception', goal: 'g2', focus: '', misconception: '헌병 경찰제를 보통 경찰제로 바꿨으면 경찰이 줄어든 거죠?', based_on: ['S2'] }
    });
    if (p.indexOf('지금 시험을 본다') >= 0) return Promise.resolve({ answers: [
      { id: 'q1', thought: '선배가 헌병이 경찰 일을 했다고 하셨지…', answer: '헌병이 경찰 일을 했다.', claims: [{ text: '헌병이 경찰 업무를 맡았다', basis: ['S1'] }], status: 'answered' },
      { id: 'q2', thought: '보통 경찰제로 바뀌었으니까… 경찰이 줄었겠지?', answer: '경찰이 줄었다.', claims: [{ text: '경찰이 줄었다', basis: ['B1'] }, { text: '신문을 검열했다', basis: [] }], status: 'partial' }] });
    if (p.indexOf('근거 검증기') >= 0) return Promise.resolve({ results: [
      { id: 'q1', claims: [{ verdict: 'ok' }], final_answer: '헌병이 경찰 일을 했다.', status: 'answered' },
      { id: 'q2', claims: [{ verdict: 'ok' }, { verdict: 'unsupported', reason: '근거 번호 없음' }], final_answer: '경찰이 줄었다.', status: 'partial' }] });
    return Promise.resolve({
      score: 55, summary: '무단 통치는 잘 가르쳤지만 문화 통치의 기만성이 전달되지 않았어요.',
      per_question: [
        { id: 'q1', items: [{ got: 4, note: '' }, { got: 0, note: '즉결 처분권이 빠짐' }, { got: 0, note: '' }], reason: '헌병이 경찰 업무를 맡았다는 핵심은 맞았지만, 재판 없이 처벌한 즉결 처분권을 쓰지 않아 깎였다.' },
        { id: 'q2', items: [{ got: 0 }, { got: 0 }, { got: 0 }, { got: 0 }], reason: '빈칸이라 점수를 줄 수 없다.' }],
      cards: [
        { tag: '오개념 미교정', title: '보통 경찰제 전환 후 경찰 수', tip: '경찰이 줄었냐는 질문에 오히려 경찰 수와 예산이 늘었다고 바로잡아 주세요.', student: '경찰이 줄었다고 답함', missing: '경찰 관서, 경찰 수, 예산은 오히려 늘었다.', cause: 'M1 추론을 바로잡지 않고 넘어갔어요.', section: 's2' },
        { tag: '참고', title: '치안 유지법 1928년 개정', student: '언급 없음', missing: '1928년 개정으로 최고형이 사형이 됐다.', cause: '세부 사항이라 감점하지 않았어요.', section: 's2' }],
      good: ['S1에서 헌병 경찰제를 정확히 설명했어요.']
    });
  };
  return Promise.resolve(f);
} };

const interviewId = localStorage.getItem('interview_id');
const scores = document.getElementById('scores');
const recommendation = document.getElementById('recommendation');
const details = document.getElementById('details');

(async function loadResults() {
  const res = await fetch(`/api/interview/${interviewId}/report`);
  const data = await res.json();
  const report = data.report;

  const cards = [
    ['Technical Score', report.technical_score],
    ['Communication Score', report.communication_score],
    ['Confidence Score', report.confidence_score],
  ];

  scores.innerHTML = cards.map(([label, val]) => `
    <div class="bg-slate-900 border border-slate-800 rounded-xl p-4">
      <p class="text-slate-400">${label}</p>
      <p class="text-3xl font-bold">${val}/10</p>
    </div>`).join('');

  recommendation.innerHTML = `<h2 class="text-xl font-semibold">Recommendation: ${report.recommendation}</h2>`;

  details.innerHTML = (report.answers || []).map((a, i) => `
    <div class="bg-slate-900 border border-slate-800 rounded-xl p-4">
      <p class="font-semibold">Q${i + 1}: ${a.question}</p>
      <p class="text-slate-300 mt-2">${a.transcript}</p>
      <p class="text-indigo-300 mt-2">Score: ${a.evaluation.score}/10</p>
      <p class="text-slate-400">${a.evaluation.feedback}</p>
    </div>`).join('');
})();

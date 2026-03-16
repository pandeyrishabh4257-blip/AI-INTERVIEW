const interviewId = localStorage.getItem('interview_id');
const transcriptBox = document.getElementById('transcript');
const questionBox = document.getElementById('questionBox');
const manualAnswer = document.getElementById('manualAnswer');
const avatar = document.getElementById('avatar');

let mediaRecorder;
let chunks = [];
let currentQuestion = '';

function addMessage(role, text) {
  const div = document.createElement('div');
  div.className = role === 'ai' ? 'text-indigo-300' : 'text-emerald-300';
  div.textContent = `${role === 'ai' ? 'AI' : 'You'}: ${text}`;
  transcriptBox.appendChild(div);
  transcriptBox.scrollTop = transcriptBox.scrollHeight;
}

function speak(text) {
  if (!text) return;
  const u = new SpeechSynthesisUtterance(text);
  avatar.classList.add('talking');
  u.onend = () => avatar.classList.remove('talking');
  speechSynthesis.speak(u);
}

async function loadQuestion() {
  const res = await fetch(`/api/interview/${interviewId}/next-question`);
  const data = await res.json();
  if (data.done) {
    window.location.href = '/results';
    return;
  }
  currentQuestion = data.question.text;
  questionBox.textContent = `${data.question.type}: ${currentQuestion}`;
  addMessage('ai', currentQuestion);
  speak(currentQuestion);
}

document.getElementById('speakBtn').onclick = () => speak(currentQuestion);

document.getElementById('startRecord').onclick = async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);
  chunks = [];
  mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
  mediaRecorder.start();
};

document.getElementById('stopRecord').onclick = () => {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') mediaRecorder.stop();
};

document.getElementById('submitAnswer').onclick = async () => {
  const fd = new FormData();
  fd.append('question', currentQuestion);

  if (chunks.length) {
    const blob = new Blob(chunks, { type: 'audio/webm' });
    fd.append('audio', blob, 'answer.webm');
  } else {
    fd.append('answer', manualAnswer.value);
  }

  const res = await fetch(`/api/interview/${interviewId}/submit-answer`, { method: 'POST', body: fd });
  const data = await res.json();
  addMessage('you', data.transcript || manualAnswer.value);
  addMessage('ai', `Score: ${data.evaluation.score}/10 | Feedback: ${data.evaluation.feedback}`);

  manualAnswer.value = '';
  chunks = [];

  if (data.done) {
    window.location.href = '/results';
  } else {
    await loadQuestion();
  }
};

loadQuestion();

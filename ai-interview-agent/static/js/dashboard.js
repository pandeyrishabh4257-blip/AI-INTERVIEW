const form = document.getElementById('resumeForm');
const preview = document.getElementById('resumePreview');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(form);
  fd.append('user_id', localStorage.getItem('user_id') || 'guest-user');

  const res = await fetch('/api/upload-resume', { method: 'POST', body: fd });
  const data = await res.json();

  if (data.ok) {
    localStorage.setItem('interview_id', data.interview_id);
    preview.classList.remove('hidden');
    preview.innerHTML = `
      <h3 class="text-xl font-semibold mb-2">Resume Extracted</h3>
      <p><strong>Name:</strong> ${data.resume.name}</p>
      <p><strong>Skills:</strong> ${(data.resume.skills || []).join(', ')}</p>
      <button id="startInterview" class="mt-4 bg-indigo-600 px-4 py-2 rounded-lg">Start Interview</button>
    `;
    document.getElementById('startInterview').onclick = () => window.location.href = '/interview';
  }
});

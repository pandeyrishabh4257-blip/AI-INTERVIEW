const form = document.getElementById('loginForm');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(form);
  const res = await fetch('/api/login', { method: 'POST', body: fd });
  const data = await res.json();
  if (data.ok) {
    localStorage.setItem('user_id', data.user_id);
    localStorage.setItem('email', data.email);
    window.location.href = '/dashboard';
  }
});

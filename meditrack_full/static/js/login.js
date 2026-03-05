// this relies on compat SDK above and firebase.initializeApp already called
const auth = firebase.auth();

document.getElementById('loginForm').addEventListener('submit', function(e){
  e.preventDefault();
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  auth.signInWithEmailAndPassword(email, password)
    .then(() => { window.location.href = '/pharmacy'; })
    .catch(err => {
      document.getElementById('alert-placeholder').innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
    });
});

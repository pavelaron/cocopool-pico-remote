(function() {
  const form = document.getElementById('form-setup');
  const btnSubmit = document.getElementById('btn-submit');
  const message = document.getElementById('message');

  form.addEventListener('submit', function(e) {
    e.preventDefault();
    btnSubmit.classList.add(hiddenClass);

    const hiddenClass = 'setup-hidden';
    const http = new XMLHttpRequest();

    http.open('POST', '/save-ssid', true);
    http.setRequestHeader('Content-Type', 'application/json');
    http.onload = function() {
      message.innerText = http.status === 200
        ? 'SSID has been saved! Please reboot your device for changes to take effect.'
        : 'Connection error! Please try again.';

      btnSubmit.classList.remove(hiddenClass);
      message.classList.remove(hiddenClass);

      form.reset();
    };

    const data = JSON.stringify({
      ssid: form.ssid.value,
      password: form.password.value,
    });

    http.send(data);
  });
})();

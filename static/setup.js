(function() {
  var form = document.getElementById('form-setup');
  var btnSubmit = document.getElementById('btn-submit');
  var message = document.getElementById('message');

  form.addEventListener('submit', function(e) {
    e.preventDefault();
    btnSubmit.classList.add(hiddenClass);

    var hiddenClass = 'setup-hidden';
    var http = new XMLHttpRequest();

    http.open('POST', '/save-ssid', true);
    http.setRequestHeader("Content-Type", "application/json");
    http.onload = function(progress) {
      message.innerText = http.status === 200
        ? 'SSID has been saved! Please reboot your device for changes to take effect.'
        : 'Connection error! Please try again.';

      btnSubmit.classList.remove(hiddenClass);
      message.classList.remove(hiddenClass);

      form.reset();
    };

    var data = JSON.stringify({
      ssid: form.ssid.value,
      password: form.password.value,
    });

    http.send(data);
  });
})();

(function() {
  const buttons = document.getElementsByClassName('button');

  for (const button of buttons) {
    button.addEventListener('click', function(e) {
      const name = e.currentTarget.name;
      const http = new XMLHttpRequest();

      http.open('GET', `/button/${name}`);
      http.send();
    });
  }
})();

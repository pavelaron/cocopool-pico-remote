(function() {
  var buttons = document.getElementsByClassName('button');

  for (var i = 0; i < buttons.length; ++i) {
    buttons[i].addEventListener('click', function(e) {
      var name = e.currentTarget.name;
      var http = new XMLHttpRequest();

      http.open('HEAD', '/button/' + name);
      http.send();
    });
  }
})();

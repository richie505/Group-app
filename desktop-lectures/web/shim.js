// Runs inside each lecture deck (an iframe of the desktop app): the deck's "Android" bridge becomes messages to the
// app's window, the app can send keys in, and the deck reports which slide it is on.
(function () {
  function post(t, x) { try { parent.postMessage(Object.assign({ t: t }, x || {}), '*'); } catch (e) {} }
  window.Android = { next: function () { post('next'); }, prev: function () { post('prev'); }, close: function () { post('close'); } };
  addEventListener('message', function (e) {
    var k = e.data && e.data.key;
    if (k) document.dispatchEvent(new KeyboardEvent('keydown', { key: k }));
  });
  addEventListener('keydown', function (e) {  // keys the app handles, pressed while the deck has the focus
    if (e.key === 'Escape' || e.key === 'f' || e.key === 'F' || e.key === 's' || e.key === 'S' || e.key === '[' || e.key === ']' || (e.key === 'k' && (e.ctrlKey || e.metaKey)) || e.key === '/') {
      e.preventDefault(); post('key', { key: e.key, ctrl: e.ctrlKey || e.metaKey });
    }
  });
  var st = document.createElement('style');
  st.textContent = '#ctl #cl{display:none!important}';   // the app has its own way back
  document.documentElement.appendChild(st);
  var iv = setInterval(function () {
    var c = document.querySelector('#ct'); if (!c) return;
    clearInterval(iv);
    var rep = function () { var m = c.textContent.match(/(\d+)\s*\/\s*(\d+)/); if (m) post('slide', { cur: +m[1], n: +m[2] }); };
    new MutationObserver(rep).observe(c, { childList: true, characterData: true, subtree: true }); rep();
  }, 100);
})();

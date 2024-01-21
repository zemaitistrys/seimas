if (!window.dash_clientside) {
  window.dash_clientside = {};
}

window.dash_clientside.clientside = {
  scrollToBottom: function (n_clicks) {
    // Check if the button was clicked
    if (n_clicks > 0) {
      console.log('Scroll to the bottom of the page');
      setTimeout(function () {
        window.scrollTo(0, document.body.scrollHeight);
      }, 500);
    }
    return window.dash_clientside.no_update; // This tells Dash to not update the associated Output
  },
};

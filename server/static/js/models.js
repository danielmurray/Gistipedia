// Models

var WikiDoc = ModelWS.extend({
  defaults: function() {
    return {
      id: null,
      zone: "home",
      type: 'analog',
      value: 0 // between 0 and 100
    }
  }
});
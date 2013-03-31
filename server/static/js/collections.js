// Collection definitions

var LightCollection = CollectionWS.extend({
  model: LightModel,
  url: '/light',
  getLightsByZone: function(zone) {
  	lightsToBeReturned = {};
  	_.each(this.models, function(model){
  		if(model.get('zone') == zone){
  			lightsToBeReturned[model.id] = model;
  		}
  	});
  	return lightsToBeReturned;
  },
  zoneData: function(zone){
    var lightson = [];

    _.each(this.models, function(model){
      if(model.get('zone') == zone && model.get('value') != 0 ){
        lightson.push(model);
      }
    });

    return [
      lightson.length,
      'Lights<br/>On'
    ]
  }
});

var BlindCollection = CollectionWS.extend({
  model: BlindModel,
  url: '/light',
  getLightsByZone: function(zone) {
    lightsToBeReturned = {};
    _.each(this.models, function(model){
      if(model.get('zone') == zone){
        lightsToBeReturned[model.id] = model;
      }
    });
    return lightsToBeReturned;
  },
  zoneData: function(zone){
    var blindopen = [];

    _.each(this.models, function(model){
      if(model.get('zone') == zone && model.get('value') != 0 ){
        blindopen.push(model);
      }
    });
   
    if(blindopen.length == 0){
      return [
        '',
        ''
      ]
    }else{
      return [
        blindopen.length,
        'Blinds<br/>Open'
      ]
    }
    
  }
});

var HVACCollection = CollectionWS.extend({
  model: HVACModel,
  url: '/hvac'
});

var PVCollection = CollectionWS.extend({
  model: PVModel,
  url: '/pv',
  _order_by: 'id',
  _descending: 1,
  comparator: function(device) {
    return this._descending * device.get(this._order_by);
  },
  _sortBy: function(orderOn,descending){
    
    if(descending)
      this._descending = -1;
    else
      this._descending = 1;

    this._order_by = orderOn;
    this.sort();
  },

  getHistoricalData: function(start,end,density) {
    
    return randomArray(start, end, density, 100);

  }
});

var DevicesCollection = CollectionWS.extend({
  model: DevicesModel,
  url: '/devices',


  _order_by: 'id',
  _descending: 1,
  comparator: function(device) {
    return this._descending * device.get(this._order_by);
  },
  _sortBy: function(orderOn,descending){
    
    if(descending)
      this._descending = -1;
    else
      this._descending = 1;

    this._order_by = orderOn;
    this.sort();
  },
  

  getHistoricalData: function(start,end,density) {
    
    return randomArray(start, end, density, 100);

  },
  zoneData: function(zone){
    var roomwatts = 0;

    _.each(this.models, function(model){
      if(model.get('zone') == zone){
        roomwatts += parseFloat(model.get('value').toFixed(0));
      }
    });
   
    return [
      roomwatts,
      'W'
    ]    
  }
});

var WaterCollection = CollectionWS.extend({
  model: WaterModel,
  url: '/water',
  _order_by: 'id',
  _descending: 1,
  comparator: function(device) {
    return this._descending * device.get(this._order_by);
  },
  _sortBy: function(orderOn,descending){
    
    if(descending)
      this._descending = -1;
    else
      this._descending = 1;

    this._order_by = orderOn;
    this.sort();
  },

  getHistoricalData: function(start,end,density) {
    
    return randomArray(start, end, density, 100);

  }
});
// Views, all inherit BaseView
var BaseView = Backbone.View.extend({
  initialize: function() {
  },

  assign: function(view, selector) {
    //console.log(view,selector)
    view.setElement(this.$(selector));
  },

  route: function(part, remaining) {
    return {};
  },

  dispose: function() {
    this.remove();
    this.off();
    if (this.model) {
      this.model.off(null, null, this);
    }
  },

  animateIn: function(){
    //console.log('No Animation In');
  },

  animateOut: function(){
    //console.log('No Animation Out');
  }
});

var HomeView = BaseView.extend({
  el: "#viewport",
  initialize: function() {
    //IMPORTANT LINE OF CODE 
    var that = this;

    this.on("assign", this.animateIn);
    this.template = loadTemplate("/static/views/home.html");


    this.render()

  },
  route: function(part, remaining) {

    if (!part) {
      navigate("gist", true); // don't trigger nav inside route
    }
  
    //id to view map
    var viewMap = {
      'gist' : GistView,
      'graph': WikiGraph
    }

    if(remaining.length == 0)
      query = 'Wikipedia'
    else{
      query = remaining[0]
    }

    //find view in id-view map
    if (viewMap[part]){
      viewToBeReturned = new viewMap[part]({query:query});
    } else {
      viewToBeReturned = new GistView()
    }

    return {
      "#homeWrapper": viewToBeReturned
    };    
  
  },
  render: function() {
    var renderedTemplate = this.template();
    this.$el.html(renderedTemplate);
  }
});

var GistView = BaseView.extend({
  el: "div",
  events: {
    "click .gistSearch":  "gistQuery",
    "submit form": "gistQuery"
  },
  initialize: function() {
    //IMPORTANT LINE OF CODE 
    var that = this;

    this.on("assign", this.animateIn);
    this.template = loadTemplate("/static/views/gist.html");

    $.ajax({
      type: 'GET',
      url: '/picoftheday',
      dataType: 'json',
      async: true,
      success: function(data){
        that.pictureOfTheDay = data
        that.injectPictureOfTheDay()
      },
      error: function(data){
        console.log('Request Failed');
      }
    });
    
    
  },
  route: function(part, remaining) {
    
    return []     
  
  },
  render: function() {
    var renderedTemplate = this.template();
    this.$el.html(renderedTemplate);
  },
  injectPictureOfTheDay: function() {
    console.log($('#homeWrapper'))
    $('#homeWrapper').css('background', 'url(\'' + this.pictureOfTheDay['url'] +'\') no-repeat center center fixed' )
    $('.gistField').val(this.pictureOfTheDay['title'])
  },
  gistQuery: function(){
    query = $('.gistField').val();
    navigate('graph/'+query, false)
  }
});

var WikiGraph = BaseView.extend({
  el: 'div',
  events: {

  },
  initialize: function(query) {
    //IMPORTANT LINE OF CODE 
    var that = this;
    
    $.ajax({
      type: 'GET',
      url: '/graph/'+query['query'],
      dataType: 'json',
      async: false,
      success: function(data){
        that.model = new WikiDoc({
          'title': data.doc.title,
          'text': data.doc.text,
          'summary': data.doc.summary,
          'image': data.doc.randomImageURL,
          'categories': data.doc.categories,
          'links': data.links
        })
      },
      error: function(data){
        console.log('Request Failed');
      }
    });

    // var randomNumber = Math.floor(Math.random()*6)
    // var tempNameArray = [
    //   'Japan',
    //   'Sumo Wrestling',
    //   'North Korea Propaganda',
    //   'Taipei',
    //   'Ludwig van Beethoven',
    //   'Xi\'an Terracotta Soldiers'
    // ]

    // this.model = new WikiDoc({
    //   'title': tempNameArray[randomNumber],
    //   'text': "Lorem Ipsum suspendisse potenti. Vestibulum rhoncus. Ut rhoncus turpis a massa. Vivamus adipiscing vestibulum nunc. Maecenas vitae lorem. Donec mi. Donec justo quam, laoreet ut, fermentum at, blandit vitae, ligula. Vestibulum diam. Etiam ut velit nec lacus consectetuer sodales. Integer accumsan. Maecenas eleifend vestibulum libero. Vestibulum metus ligula, volutpat vitae, feugiat at, blandit quis, lorem. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Fusce varius scelerisque est. Aliquam turpis dui, eleifend in, elementum vel, porta vitae, velit. Cras hendrerit vehicula enim. Sed auctor. In hac habitasse platea dictumst. Nulla lectus. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Donec accumsan ante non leo. Donec sollicitudin mi et magna. Proin non est. Vestibulum diam. Quisque in enim. Sed id dui. Nunc nec sapien. Nulla lacus. Quisque in ante vel nunc semper pellentesque. Nam sit amet lacus sit amet ipsum auctor eleifend. Quisque vitae justo eu neque mattis pellentesque. Suspendisse tristique. Nulla facilisi. Pellentesque hendrerit tristique turpis. Pellentesque eget mi. Vestibulum a lacus. Lorem Ipsum suspendisse potenti. Vestibulum rhoncus. Ut rhoncus turpis a massa. Vivamus adipiscing vestibulum nunc. Maecenas vitae lorem. Donec mi. Donec justo quam, laoreet ut, fermentum at, blandit vitae, ligula. Vestibulum diam. Etiam ut velit nec lacus consectetuer sodales. Integer accumsan. Maecenas eleifend vestibulum libero. Vestibulum metus ligula, volutpat vitae, feugiat at, blandit quis, lorem. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Fusce varius scelerisque est. Aliquam turpis dui, eleifend in, elementum vel, porta vitae, velit. Cras hendrerit vehicula enim. Sed auctor. In hac habitasse platea dictumst. Nulla lectus. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Donec accumsan ante non leo. Donec sollicitudin mi et magna. Proin non est. Vestibulum diam. Quisque in enim. Sed id dui. Nunc nec sapien. Nulla lacus. Quisque in ante vel nunc semper pellentesque. Nam sit amet lacus sit amet ipsum auctor eleifend. Quisque vitae justo eu neque mattis pellentesque. Suspendisse tristique. Nulla facilisi. Pellentesque hendrerit tristique turpis. Pellentesque eget mi. Vestibulum a lacus.",
    //   'image': 'static/images/' + randomNumber + '.jpg',
    //   'categories': [
    //     'Asian Country',
    //     'Super Power',
    //     'Weird Porn',
    //     'Anime',
    //     'Economically Stable',
    //     'First World Country'
    //   ],
    //   'links': [
    //     'Asian Country',
    //     'Super Power',
    //     'Weird Porn',
    //     'Anime',
    //     'Economically Stable',
    //     'First World Country'
    //   ]
    // });

    this.on("assign", this.animateIn);
    this.template = loadTemplate("/static/views/wikigraph.html");
    
  },
  route: function(part, remaining) {
    
    wikinode = new WikiNode({model: this.model})
    
    return {
      "#wikiNodeWrapper": wikinode
    };
    

  },
  render: function() {
    var renderedTemplate = this.template({model:this.model});
    this.$el.html(renderedTemplate);
  }
});

var WikiNode = BaseView.extend({
  el: 'div',
  initialize: function(model) {
    //IMPORTANT LINE OF CODE 
    var that = this;
    this.model = model['model']
    this.on("assign", this.animateIn);
    this.template = loadTemplate("/static/views/wikinode.html");
    
  },
  route: function(part, remaining) {

    categorytable = new TableView({collection: this.model.get('categories')})
    linktable = new TableView({collection: this.model.get('links')})

    return {
      "#nodeCategories": categorytable,
      "#nodeLinks": linktable
    }  
    

  },
  render: function() {
    var renderedTemplate = this.template({model:this.model});
    this.$el.html(renderedTemplate);
  },
  animateIn: function(click){
    
    // if(!this.currentpane)
    //   return;

    // var slider = $('.' + this.currentpane.id + '.icon-nav .slider');
    // slider.animate({
    //   width: '100%'
    // },{
    //   duration: 500, 
    //   queue: true
    // });

  }
});

var TableView = BaseView.extend({
  el: 'div',
  initialize: function(data) {
    this.template = loadTemplate("/static/views/table.html");
    this.collection = data.collection;
  },
  route: function(part) {
    var that = this;

    //pointers for this view
    this.tableEntries = {};

    //views to be returned
    tableEntriesToRendered = {};

    _.each(this.collection, function(model,i) {
      tableentry = new TableViewEntry({model: model});
      tableEntriesToRendered['#tableEntry'+i] = tableentry;
      that.tableEntries[model] = {};
      that.tableEntries[model].id = model;
      that.tableEntries[model].view = tableentry;
      that.tableEntries[model].model = model;

    });


    console.log(tableEntriesToRendered)

    return tableEntriesToRendered;
  },
  render: function() {
    var renderedTemplate = this.template({collection: this.collection});
    this.$el.html(renderedTemplate);
  }
});

var TableViewEntry = BaseView.extend({
  el: 'div',
  initialize: function(data) {
    this.template = loadTemplate("/static/views/tableentry.html");
    this.words = data.model;
  },
  route: function(part) {
    return {};
  },
  render: function() {
    var renderedTemplate = this.template({model:this.words});
    this.$el.html(renderedTemplate);
  }
});
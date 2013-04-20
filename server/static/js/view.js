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

    this.width = window.screen.height;
    this.height= window.screen.width;

    this.$el.height(this.height)

    this.render()

  },
  route: function(part, remaining) {

    if (!part) {
      navigate("gist", false); // don't trigger nav inside route
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

    this.width = window.screen.height;
    this.height= window.screen.width;

    this.$el.height(this.height)
    // this.$el.width(this.width)

    $.ajax({
      type: 'GET',
      url: '/picoftheday',
      dataType: 'json',
      async: true,
      success: function(data){
        that.pictureOfTheDay = data
        that.injectPictureOfTheDay(data)
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
    $('.gistPage').css('background', 'url(\'' + this.pictureOfTheDay['url'] +'\') no-repeat center center fixed' )
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
          'image': data.doc.randomImageURL,
          'categories': data.doc.categories,
          'links': data.links
        })
      },
      error: function(data){
        console.log('Request Failed');
      }
    });

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
    
    return []  
    

  },
  render: function() {
    console.log(this.model)
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
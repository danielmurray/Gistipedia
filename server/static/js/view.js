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
    "mouseover .wikiNode":  "highlight",
  },
  initialize: function(query) {
    //IMPORTANT LINE OF CODE 
    var that = this;
    this.graphNodeCount = 25
    this.nodeRadius = 50
    this.nodeExpanded= 200

    this.nodes = []
    this.node = function (link, index){
      this.id = "#wikiNode" + index;
      this.name = link ;
      this.text = link.toUpperCase();
      this.x = 0;
      this.y = 0;
      this.graph = that
      this.radius = this.graph.nodeRadius
      this.expanded = this.graph.nodeExpanded

      this.placeNodeCoord = function(x, y){
        $(this.id).fadeOut()
        this.x = x
        this.y = y
        xLeft = this.graph.xOrigin + x * this.graph.xScale - this.expanded/2
        yTop = this.graph.yOrigin + y * this.graph.yScale - this.expanded/2

        $(this.id).css('left',xLeft)
        $(this.id).css('top',yTop)
        $(this.id).fadeIn(500) 
      }
    }

    this.template = loadTemplate("/static/views/wikigraph.html");
    
    this.docRequest(query['query'],this.graphNodeCount)

    this.on("assign", this.animateIn);
    
  },
   route: function(part, remaining) {
    
    viewsToReturn = {}

    viewsToReturn["#wikiDetailWrapper"] = new WikiDetail({model: this.model})
    
    for( var i = 0; i < this.nodes.length; i++){
      node = this.nodes[i]
      viewsToReturn[node.id] = new WikiNode(node)
    }

    return viewsToReturn;
    

  },
  render: function() {
    that = this
    
    var renderedTemplate = this.template({
      nodes:this.nodes,
      nodeExpanded:this.nodeExpanded
    });

    this.$el.html(renderedTemplate);

    setTimeout(function(){
      that.initGraph()
    }, 6000);

  },
  highlight: function(click){

  },
  docRequest: function (query,doccount) {
    that = this
    $.ajax({
      type: 'GET',
      data: "query=" + query + '&doccount=' + doccount,
      url: '/root/',
      dataType: 'json',
      async: false,
      success: function(data){
        console.log(data)
        that.model = new WikiDoc({
          'title': data.doc.title,
          'text': data.doc.text,
          'summary': data.doc.summary,
          'image': data.doc.randomImage,
          'categories': data.doc.categories,
          'links': data.doc.links
        })
        console.log(that.model)
        that.initNodes()
      },
      error: function(data){
        console.log('Request Failed');
      }
    });
  },
  initNodes:function(){
    console.log(this)
    nodeLength = (this.graphNodeCount < this.model.get('links').length) ? this.graphNodeCount : this.model.get('links').length
    for ( var i=0; i < nodeLength; i++){
      link = this.model.get('links')[i][0]
      node = new this.node(link, i)
      this.nodes.push(node)
    }
  },
  initGraph:function(){
    this.xWidth = that.$('#graphWrapper').width()
    this.yHeight = that.$('#graphWrapper').height()
    this.xOrigin = this.xWidth/2
    this.yOrigin = this.yHeight/2

    //Essentially Pixels per X or Y value
    this.xScale = this.xWidth / 200
    this.yScale = this.yHeight / 200

    //Circle Implementation
    pieSliceDegree = 360/this.graphNodeCount

    for ( var i=0; i < this.nodes.length; i++){
      node = this.nodes[i]
      $(node.id).css('position', 'absolute')
      theta = (pieSliceDegree*i-90)/180 * Math.PI
      x = Math.cos(theta)
      y = Math.sin(theta)
      xScale = Math.random() * 90
      yScale = Math.random() * 90
      // xScale = yScale = 80
      node.placeNodeCoord(x*xScale, y*yScale)
    }

  }
});

var WikiNode = BaseView.extend({
  el: 'div',
  initialize: function( data ) {
    //IMPORTANT LINE OF CODE 
    var that = this;

    this.rootTitle = data.graph.model.get('title')
    this.model = new WikiDoc({
      'id': data.id,
      'name': data.name, 
      'title': data.text,
      'radius': data.radius,
      'expanded':data.expanded
    })

    this.nodeRequest(this.rootTitle, this.model.get('name'), this.model.get('id') + ' .wikiNode')    

    this.on("assign", this.animateIn);
    this.template = loadTemplate("/static/views/wikinode.html");
    
  },
  nodeRequest: function (rootTitle, nodeTitle, target) {
    theOtherThing = this
    $.ajax({
      type: 'GET',
      data: "root=" + escape(rootTitle) + '&node=' + escape(nodeTitle) ,
      url: '/node/',
      dataType: 'json',
      async: true,
      success: function(data){
        theOtherThing.model.set({
          'thumb': data.thumb,
          'thumbSmall': data.thumbSmall
        })
        $(target).css(
          'background', 'rgba(240,240,240,1) url(' + theOtherThing.model.get('thumbSmall') + ') no-repeat center center'
        )
      },
      error: function(data){
        console.log('Request Failed');
      }
    });
  },
  route: function(part, remaining) {

    return {}  
    

  },
  render: function() {
    var renderedTemplate = this.template({model:this.model});
    this.$el.html(renderedTemplate);
  }
});

var WikiDetail = BaseView.extend({
  el: 'div',
  initialize: function(model) {
    //IMPORTANT LINE OF CODE 
    var that = this;
    this.model = model['model']
    this.template = loadTemplate("/static/views/wikidetail.html");
    
  },
  route: function(part, remaining) {

    return {}  
    

  },
  render: function() {
    var renderedTemplate = this.template({model:this.model});
    this.$el.html(renderedTemplate);
  }
});
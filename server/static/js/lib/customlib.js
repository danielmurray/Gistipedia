function retrieveView(pane){
  
  var viewMap = {
    'home' : StatusView,
    'lights': LightView,
    'power': PowerView
  }
  console.log(pane)
  if (viewMap[pane.id]){
    viewToBeReturned = new viewMap[pane.id](pane);
  } else {
    viewToBeReturned = new PageView(pane);
  }

  return viewToBeReturned;
}


var cachedTemplates = {};
function loadTemplate(url) {

  if (cachedTemplates[url]) {
    return cachedTemplates[url];
  }

  var text;
 
  $.ajax({
   url: url,
   success: function(t) {
     //console.log(t);
     text = t;
   },
   error: function() {
       console.log('hello world')
   },
   async: false
  });
  var tpl = _.template(text);
  cachedTemplates[url] = tpl;
  return tpl;
}

function loadData(url) {
   var data;
   $.ajax({
       url: url,
       success: function(d) {
           //console.log(d);
           data = d;
       },
       error: function() {
           return false;
       },
       async: false,
       dataType: "text"
    });
  return data;
}

var componentToHex = function(c) {
   var hex = c.toString(16);
   return hex.length == 1 ? "0" + hex : hex;
}

var rgbToHex = function(color) {
  r = color.r;
  g = color.g;
  b = color.b;

  if( r=="" ) r=0;
  if( g=="" ) g=0;
  if( b=="" ) b=0;
  if( r<0 ) r=0;
  if( g<0 ) g=0;
  if( b<0 ) b=0;
  if( r>255 ) r=255;
  if( g>255 ) g=255;
  if( b>255 ) b=255;

   return componentToHex(r) + componentToHex(g) + componentToHex(b);
}

var hexToRgb = function(hex) {
   var shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
   hex = hex.replace(shorthandRegex, function(m, r, g, b) {
       return r + r + g + g + b + b;
   });

   var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
   return result ? {
       r: parseInt(result[1], 16),
       g: parseInt(result[2], 16),
       b: parseInt(result[3], 16)
   } : null;
}

var randomArray = function(start, end, size, seed){

  var arr = [];

  var now = start;
  var then = end;

  step = (now-then)/size;
  arr[0] = [];
  arr[0][0] = then;
  arr[0][1] = Math.random() * seed;

  for(var i=1; i<size; i++){
    arr[i] = [];
    arr[i][0] = then + step *i;
    
    arr[i][1] = arr[i-1][1] + (Math.random()*2 - 1)
  }


  return arr;
}

var rgbaToString = function(color,opacity){
  
  var thing = 'rgba(' + color[0] + ',' + color[1] + ',' + color[2]  + ',' + opacity + ')';

  return thing;
}

var hslToRgb = function(color){
  h = color.h
  s = color.s;
  l = color.l;

  if( h=="" ) h=0;
  if( s=="" ) s=0;
  if( l=="" ) l=0;
  if( h<0 ) h=0;
  if( s<0 ) s=0;
  if( l<0 ) l=0;
  if( h>=360 ) h=359;
  if( s>1 ) s=1;
  if( l>1 ) l=1;

  C = (1-Math.abs(2*l-1))*s;
  hh = h/60;
  X = C*(1-Math.abs(hh%2-1));
  r = g = b = 0;
  
  if( hh>=0 && hh<1 ) {
    r = C;
    g = X;
  } else if( hh>=1 && hh<2 ) {
    r = X;
    g = C;
  }
  else if( hh>=2 && hh<3 ) {
    g = C;
    b = X;
  } else if( hh>=3 && hh<4 ) {
    g = X;
    b = C;
  } else if( hh>=4 && hh<5 ) {
    r = X;
    b = C;
  } else {
    r = C;
    b = X;
  }

  m = l-C/2;
  r += m;
  g += m;
  b += m;
  r *= 255;
  g *= 255;
  b *= 255;

  r = Math.floor(r);
  g = Math.floor(g);
  b = Math.floor(b);

  return {
    'r': r,
    'g': g,
    'b': b
  }              
}

var rgbToHsl = function(color){
  r = color.r;
  g = color.g;
  b = color.b;

  if( r=="" ) r=0;
  if( g=="" ) g=0;
  if( b=="" ) b=0;
  if( r<0 ) r=0;
  if( g<0 ) g=0;
  if( b<0 ) b=0;
  if( r>255 ) r=255;
  if( g>255 ) g=255;
  if( b>255 ) b=255;

  r/=255;
  g/=255;
  b/=255;
  M = Math.max(r,g,b);
  m = Math.min(r,g,b);
  d = M-m;
  
  if( d==0 ) 
    h=0;
  else if( M==r ) 
    h=((g-b)/d)%6;
  else if( M==g ) 
    h=(b-r)/d+2;
  else 
    h=(r-g)/d+4;
  
  h*=60;
  
  if( h<0 ) 
    h+=360;
  
  l = (M+m)/2;
  
  if( d==0 )
    s = 0;
  else
    s = d/(1-Math.abs(2*l-1));

  return {
    'h': h,
    's': s,
    'l': l
  } 
}


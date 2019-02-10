
var stockApp = angular.module('stockangApp', ['angularUtils.directives.dirPagination',"ui.grid",'ui.grid.pagination', 'ui.grid.resizeColumns', "ngAnimate","ngAria",'ngMaterial','nvd3','ngSanitize']);   
if (typeof Object.keys !== "function") {
    (function() {
        var hasOwn = Object.prototype.hasOwnProperty;
        Object.keys = Object_keys;
        function Object_keys(obj) {
            var keys = [], name;
            for (name in obj) {
                if (hasOwn.call(obj, name)) {
                    keys.push(name);
                }
            }
            return keys;
        }
    })();
}


stockApp.controller('portfolioCtrl', function ($scope, $http) {
  $scope.currentNavItem = 'portfolio';
  $scope.sortType     = 'symbol'; // set the default sort type
  $scope.sortReverse  = false; 
  $scope.search ='' 
  $scope.add ='' 

 $http.get('/api/getportfolio').success(function(data) {


$scope.stocks = JSON.parse(data.data);
$scope.stockkeys = Object.keys($scope.stocks[0]);
$scope.defaultcolumns = ['symbol', 'buydate','buyprice','quantity', 'CLOSE',   'last_close_100_ema'   , 'last_close_50_ema' ,  'close_50_ema_xd_close_100_ema', 'close_LT_100_ema', 'close_LT_50_ema','close_50_ema_xu_close_100_ema', 'gainpercent', 'comments', 'buyholdsell']
$scope.displaycolumns = $scope.defaultcolumns
$scope.addablecolumns = $scope.stockkeys.filter(function(x) { return $scope.displaycolumns.indexOf(x) < 0 })
$scope.toggleSelection = function toggleSelection(stock) {
    var idx = $scope.displaycolumns.indexOf(stock);

    // Is currently selected
    if (idx > -1) {
      $scope.displaycolumns.splice(idx, 1);
    }

    // Is newly selected
    else {
      $scope.displaycolumns.push(stock);
    }
    $scope.selectall = 0
    $scope.clearall = 0
  };
 $scope.togglecheckall = function togglecheckall() {
    $scope.displaycolumns = $scope.stockkeys
    
    $scope.clearall = 0
  };
   $scope.toggleclearall = function togglecheckall() {
    $scope.displaycolumns = $scope.defaultcolumns
    $scope.selectall = 0
    
  };
$scope.searchkeys= $scope.stockkeys.map(function(x){
    return "search."+x;
});

});  // end of http call
$scope.changesort = function(key){
    
    $scope.sortType = key
    $scope.sortReverse  = !$scope.sortReverse; 
  };
 $scope.addStock = function(){

   $http.get('/api/add/portfoliostock?symbol='+$scope.add.symbol+'&buyprice='+$scope.add.buyprice+'&buydate='+$scope.add.buydate+'&quantity='+$scope.add.quantity+'&comments='+$scope.add.comments+'&buyholdsell='+$scope.add.buyholdsell).success(function(data) {
      
        $http.get('/api/getportfolio').success(function(data) {

            $scope.stocks = JSON.parse(data.data);
            $scope.add = '';
        });
      
     });
  
  };
   $scope.deleteStock = function(symbol){

   $http.get('/api/delete/portfoliostock?symbol='+symbol).success(function(data) {
      
        $http.get('/api/getportfolio').success(function(data) {

            $scope.stocks = JSON.parse(data.data);
        });
      
     });
  
  };
});



 /*stockApp.controller('AppCtrl', function($scope) {
    $scope.currentNavItem = 'page1';
  });*/
stockApp.controller('stockListCtrl', function ($scope, $http) {
  $scope.currentNavItem = 'stockdata';
  $scope.sortType     = 'SYMBOL'; // set the default sort type
  $scope.sortReverse  = false; 
  $scope.search =''	
 $http.get('/api/stockdata').success(function(data) {


$scope.stocks = JSON.parse(data.data);
$scope.stockkeys = Object.keys($scope.stocks[0]);
$scope.searchkeys= $scope.stockkeys.map(function(x){
    return "search."+x;
});

});  // end of http call
$scope.changesort = function(key){
    
    $scope.sortType = key
    $scope.sortReverse  = !$scope.sortReverse; 
  };
});

stockApp.controller('momentumCtrl', function ($scope, $http, uiGridConstants) {
  $scope.currentNavItem = 'momentum';
  $scope.sortType     = 'symbol'; // set the default sort type
  $scope.sortReverse  = false; 
  $scope.search ='' 
  $scope.gridOptions = {
    paginationPageSizes: [25, 50, 75],
    enableFiltering: true,
    paginationPageSize: 25,
    data :[],
    columnDefs: [
      {field: 'symbol'},
      {field: 'CLOSE',type: 'number', filters: [
        {
          condition: uiGridConstants.filter.GREATER_THAN,
          placeholder: 'greater than'
        }
      ]
    },
      
      { field: 'slope30',type: 'number', filters: [
        {
          condition: uiGridConstants.filter.GREATER_THAN,
          placeholder: 'greater than'
        }
      ]
    },
      { field: 'updownratio', filters: [
        {
          condition: uiGridConstants.filter.GREATER_THAN,
          placeholder: 'greater than 0.7'
        }
      ]
    },
    { field: 'greenonniftyred', filters: [
        {
          condition: uiGridConstants.filter.GREATER_THAN,
          placeholder: 'greater than 0.3'
        }
      ]
    },
    { field: 'last_pgo', filters: [
        {
          condition: uiGridConstants.filter.GREATER_THAN,
          placeholder: 'greater than'
        }
      ]
    },
      {field: 'pgo_gt_3'},
      {field: 'goldcross'},
      {field: 'higherlow'},
      {field: 'higherlowdt'},
      {field: 'close_100_ema'},
      {field: 'close_50_ema'},
      {field: 'last_close_100_ema'},
      {field: 'last_close_50_ema'},
      {field: 'timestamp'},
      {field: 'tottrdqty'},
      {field: 'momscore12',type: 'number'},
      {field: 'momscore6',type: 'number'},
      {field: 'momscore3',type: 'number'}
      
    ]
  };
 $http.get('/api/momentumscan').success(function(data) {

$scope.gridOptions.data = JSON.parse(data.data);
$scope.stocks = JSON.parse(data.data);
$scope.stockkeys = Object.keys($scope.stocks[0]);
console.log($scope.stockkeys)
$scope.searchkeys= $scope.stockkeys.map(function(x){
    return "search."+x;
});

});  // end of http call
$scope.changesort = function(key){
    
    $scope.sortType = key
    $scope.sortReverse  = !$scope.sortReverse; 
  };
$scope.searchStock = function(item){
    if ($scope.updownratiovalue) {
      
        return item.updownratio >= $scope.updownratiovalue;
    }
    if ($scope.slope30) {
      
        return item.slope30 >= $scope.slope30;
    }
    if ($scope.greenonniftyred) {
      
        return item.greenonniftyred >= $scope.greenonniftyred;
    }

    
      return true

    
  };
});

stockApp.controller('adminCtrl', function ($scope, $http) {

  $scope.currentNavItem = 'admin';

   $http.get('/api/lastloadedtime').success(function(data) {


$scope.lastdataloaded = data



});
$http.get('/api/momentumlastloadedtime').success(function(data) {


$scope.momentumlastdataloaded = data



});

   $scope.loadData = function(){
    $http.get('/api/loaddata').success(function() {


   $http.get('/api/lastloadedtime').success(function(data) {


$scope.lastdataloaded = data



});



});
    
  };
   $scope.loadmomentumData = function(){
    $http.get('/api/generatemomentum').success(function() {


   $http.get('/api/momentumlastloadedtime').success(function(data) {


$scope.momentumlastdataloaded = data



});



});
    
  };

  });



stockApp.controller('oiCtrl', function ($scope, $http) {
  $scope.sortType     = 'nse_symbol'; // set the default sort type
  $scope.sortReverse  = false; 
  $scope.search ='' 
  $scope.news = {}
 $scope.fetchNews = function(stock){

   $http.get('/api/news/'+stock).success(function(data) {
      
      $scope.news[stock] = data;
      
     });
  
  };

 $http.get('/api/eoddata/30').success(function(data) {
$scope.stocks = JSON.parse(data.data);
$scope.stockkeys = Object.keys($scope.stocks[0]);
$scope.displaycolumns = ['nse_symbol', 'nse_date','nse_fut_close','nse_open_int', 'nse_chg_in_oi',   'nse_mwpl'   , 'nse_open_interest' ,  'nse_limit_for_next_day','nse_pct_delivery_to_traded','tot_chg_oi','tot_priper_chg','oi_3d_sum','priceper_3d_sum','status','open_int_analysis']
$scope.addablecolumns = $scope.stockkeys.filter(function(x) { return $scope.displaycolumns.indexOf(x) < 0 })
$scope.lbs = $scope.stocks.filter(function(x) { return x.status == 'LB' })
$scope.sbs = $scope.stocks.filter(function(x) { return x.status == 'SB' })
$scope.lus = $scope.stocks.filter(function(x) { return x.status == 'LU' })
$scope.scs = $scope.stocks.filter(function(x) { return x.status == 'SC' })
// $scope.addablecolumns =list(set($scope.stockkeys) - set($scope.displaycolumns))  



$scope.searchkeys= $scope.stockkeys.map(function(x){
    return "search."+x;
});

}); 
 $scope.changesort = function(key){
    
    $scope.sortType = key
    $scope.sortReverse  = !$scope.sortReverse; 
  };
});

stockApp.controller('eodCtrl', function ($scope, $http) {
  $scope.sortType     = 'nse_symbol'; // set the default sort type
  $scope.sortReverse  = false; 
  $scope.search ='' 
  $scope.days = 30
  $scope.news = {}
   $scope.fetchNews = function(stock){

   $http.get('/api/news/'+stock).success(function(data) {
      
      $scope.news[stock] = data;
      
     });
  
  };
  $scope.getStockData = function getStockData() {
    symbol = $scope.nse_symbol
    if ($scope.nse_symbol && $scope.nse_symbol.includes("&")) {
      symbol = $scope.nse_symbol.replace("&", "%26");
    }  
     $scope.fetchNews(symbol);
    
 $http.get('/api/eoddata/'+$scope.days+'?nse_symbol='+symbol).success(function(data) {


$scope.stocks = JSON.parse(data.data);
$scope.stockkeys = Object.keys($scope.stocks[0]);
  $scope.options = {
            chart: {
                type: 'candlestickBarChart',
                height: 450,
                margin : {
                    top: 20,
                    right: 20,
                    bottom: 66,
                    left: 60
                },
                x: function(d){ return d['date']; },
                y: function(d){ return d['close']; },
                duration: 100,
                
                xAxis: {
                    axisLabel: 'Dates',
                    tickFormat: function(d) { 
                      
                      return d3.time.format('%x')(new Date(d));
                  }
                    
                },

                yAxis: {
                    axisLabel: 'Stock Price',
                    tickFormat: function(d){
                        
                        return  d3.format(',.1f')(d);
                    },
                    showMaxMin: false
                },
                zoom: {
                    enabled: true,
                    scaleExtent: [1, 10],
                    useFixedDomain: false,
                    useNiceScale: false,
                    horizontalOff: false,
                    verticalOff: true,
                    unzoomEventType: 'dblclick.zoom'
                }
            }
        };
  $scope.oioptions = {
            chart: {
                type: 'discreteBarChart',
                height: 450,
                margin : {
                    top: 20,
                    right: 20,
                    bottom: 66,
                    left: 60
                },
                x: function(d){ return d['date']; },
                y: function(d){ return d['oichange']; },
                duration: 100,
                
                xAxis: {
                    axisLabel: 'Dates',
                    tickFormat: function(d) { 
                      
                      return d3.time.format('%x')(new Date(d));
                  }
                    
                },

                yAxis: {
                    axisLabel: 'Open Interest Change',
                    tickFormat: function(d){
                        
                        return  d;
                    },
                    showMaxMin: false
                },
                zoom: {
                    enabled: true,
                    scaleExtent: [1, 10],
                    useFixedDomain: false,
                    useNiceScale: false,
                    horizontalOff: false,
                    verticalOff: true,
                    unzoomEventType: 'dblclick.zoom'
                },
                color: function (d, i) {
                  
                  if (d['oichange'] > 0 && d['prichange'] > 0) {
                    return "GREEN";
                  } else if (d['oichange'] < 0 && d['prichange'] > 0) {
                    return "YELLOW";
                  } else if (d['oichange'] > 0 && d['prichange'] < 0) {
                    return "RED";
                  } else if (d['oichange'] < 0 && d['prichange'] < 0) {
                    return "ORANGE";
                  } 
                  
                  return "BLUE";
                 },
                title: {
                enable: true,
                text: 'GREEN - LB  ,   YELLOW - SC ,    ORANGE -  LU , RED  -  SB'
              },
            subtitle: {
                enable: true,
                text: 'Subtitle for simple line chart. Lorem ipsum dolor sit amet, at eam blandit sadipscing, vim adhuc sanctus disputando ex, cu usu affert alienum urbanitas.',
                css: {
                    'text-align': 'center',
                    'margin': '10px 13px 0px 7px'
                }
            },
            caption: {
                enable: true,
                html: '<b>Figure 1.</b> Lorem ipsum dolor sit amet, at eam blandit sadipscing, <span style="text-decoration: underline;">vim adhuc sanctus disputando ex</span>, cu usu affert alienum urbanitas. <i>Cum in purto erat, mea ne nominavi persecuti reformidans.</i> Docendi blandit abhorreant ea has, minim tantas alterum pro eu. <span style="color: darkred;">Exerci graeci ad vix, elit tacimates ea duo</span>. Id mel eruditi fuisset. Stet vidit patrioque in pro, eum ex veri verterem abhorreant, id unum oportere intellegam nec<sup>[1, <a href="https://github.com/krispo/angular-nvd3" target="_blank">2</a>, 3]</sup>.',
                css: {
                    'text-align': 'justify',
                    'margin': '10px 13px 0px 7px'
                }
            }

            }
        };


    if($scope.stocks)    {
    values =  $scope.stocks.map(function(stock){
      return {"date": new Date(stock['nse_date']).getTime(), "open": stock['nse_open'], "high": stock['nse_high'], "low": stock['nse_low'], "close": stock['nse_close'], 'oi':stock['nse_open_interest'],'prichange': stock['nse_fut_change'],'oichange': stock['nse_chg_in_oi']}
    })
    $scope.data= [{"values": [...values]}]
    
    }

/*$scope.colums = $scope.stockkeys.map(function(x){
  return {name: x, display:true};
});
console.log($scope.colums)*/
$scope.defaultcolumns = ['nse_symbol', 'nse_date','nse_fut_close','nse_open_int', 'nse_chg_in_oi',   'nse_mwpl'   , 'nse_open_interest' ,  'nse_limit_for_next_day','nse_pct_delivery_to_traded','tot_chg_oi','tot_priper_chg','oi_3d_sum','priceper_3d_sum','status','open_int_analysis']
$scope.displaycolumns = $scope.defaultcolumns
$scope.addablecolumns = $scope.stockkeys.filter(function(x) { return $scope.displaycolumns.indexOf(x) < 0 })
$scope.toggleSelection = function toggleSelection(stock) {
    var idx = $scope.displaycolumns.indexOf(stock);

    // Is currently selected
    if (idx > -1) {
      $scope.displaycolumns.splice(idx, 1);
    }

    // Is newly selected
    else {
      $scope.displaycolumns.push(stock);
    }
    $scope.selectall = 0
    $scope.clearall = 0
  };
 $scope.togglecheckall = function togglecheckall() {
    $scope.displaycolumns = $scope.stockkeys
    
    $scope.clearall = 0
  };
   $scope.toggleclearall = function togglecheckall() {
    $scope.displaycolumns = $scope.defaultcolumns
    $scope.selectall = 0
    
  };
$scope.searchkeys= $scope.stockkeys.map(function(x){
    return "search."+x;
});

}); 
 $scope.changesort = function(key){
    
    $scope.sortType = key
    $scope.sortReverse  = !$scope.sortReverse; 
  };



}});

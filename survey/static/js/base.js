$(window).on('scroll',function(){
    var wscroll = $(this).scrollTop();
    if(wscroll > 10){
     $(".navbar").addClass("shrink-nav");
    }
    else{
      $(".navbar").removeClass("shrink-nav");
    }
  });
$(".tag").click(function() {
	$($(this).next()).css("display", "inherit")
  $($(this).next()).find("div").addClass("is-active");  
});

$(".modal-close").click(function() {
	$($(this).parent()).parent().css("display", "none");
   $(".modal").removeClass("is-active");
});

$(".reviewButton").click(function(){
	if($($($($($(this).parent()).parent()).parent()).next()).css("display")==="none"){
		$($($($($(this).parent()).parent()).parent()).next()).css("display", "inherit");
	}else{
		$($($($($(this).parent()).parent()).parent()).next()).css("display", "none");
	}
	
});
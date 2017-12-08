$(".tag").click(function() {
	console.log($(".tag").find("div")[0]);
  $(".tag").find("div")[0].find("div").addClass("is-active");  
});

$(".modal-close").click(function() {
   $(".modal").removeClass("is-active");
});
$(".tag").click(function() {
	console.log($($(this).next()).find("div"));
  $($(this).next()).find("div").addClass("is-active");  
});

$(".modal-close").click(function() {
   $(".modal").removeClass("is-active");
});
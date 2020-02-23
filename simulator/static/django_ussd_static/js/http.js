

$(document).ready(function() {
	$("#devtools").click(function(){
		$(".ussd-output").slideToggle("slow", function(){
			$("#devtools").html($(this).is(":hidden") ? "Dev Tools" : "Dev Tools");
		});
	});

	$("#user_input").focus();

});
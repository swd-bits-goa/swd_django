$(function(){
	$('#name').keyup(function() {
		$.ajax({
			type: "POST",
			url: "/search/",
			data: {
				'name' : $('#name').val(),
				'bitsid' : $('#bitsid').val(),
				'hostel' : $('#hostel').val(),
				'roomno' : $('#roomno').val(),
				'branch' : $('#branch').val(),
				'page': 1,
				'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()

			},
			success: searchSuccess,
			dataType: 'html'
		});
	});
});

$(function(){
	$('#bitsid').keyup(function() {
		$.ajax({
			type: "POST",
			url: "/search/",
			data: {
				'name' : $('#name').val(),
				'bitsid' : $('#bitsid').val(),
				'hostel' : $('#hostel').val(),
				'roomno' : $('#roomno').val(),
				'branch' : $('#branch').val(),
				'page': 1,
				'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()

			},
			success: searchSuccess,
			dataType: 'html'
		});
	});
});

$(function(){
	$('#hostel').keyup(function() {
		$.ajax({
			type: "POST",
			url: "/search/",
			data: {
				'name' : $('#name').val(),
				'bitsid' : $('#bitsid').val(),
				'hostel' : $('#hostel').val(),
				'roomno' : $('#roomno').val(),
				'branch' : $('#branch').val(),
				'page': 1,
				'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()

			},
			success: searchSuccess,
			dataType: 'html'
		});
	});
});

$(function(){
	$('#roomno').keyup(function() {
		$.ajax({
			type: "POST",
			url: "/search/",
			data: {
				'name' : $('#name').val(),
				'bitsid' : $('#bitsid').val(),
				'hostel' : $('#hostel').val(),
				'roomno' : $('#roomno').val(),
				'branch' : $('#branch').val(),
				'page': 1,
				'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()

			},
			success: searchSuccess,
			dataType: 'html'
		});
	});
});

$(function(){
	$('#branch').keyup(function() {
		$.ajax({
			type: "POST",
			url: "/search/",
			data: {
				'name' : $('#name').val(),
				'bitsid' : $('#bitsid').val(),
				'hostel' : $('#hostel').val(),
				'roomno' : $('#roomno').val(),
				'branch' : $('#branch').val(),
				'page': 1,
				'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()

			},
			success: searchSuccess,
			dataType: 'html'
		});
	});

});

// $(function(){
// 	$('.page').click(function() {
// 		$.ajax({
// 			type: "POST",
// 			url: "/search/",
// 			data: {
// 				'name' : $('#name').val(),
// 				'bitsid' : $('#bitsid').val(),
// 				'hostel' : $('#hostel').val(),
// 				'roomno' : $('#roomno').val(),
// 				'branch' : $('#branch').val(),
// 				'page': $(this).data("page"),
// 				'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").val()

// 			},
// 			success: searchSuccess,
// 			dataType: 'html'
// 		});
// 	});

// });

function searchSuccess(data, textStatus, jqXHR)
{
	$('#search-results').html(data);
}
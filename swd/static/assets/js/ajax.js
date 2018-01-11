$(function(){
	$('#search').onkeyup(function() {
		$.ajax({
			type: "POST",
			url: "/search/"
			data: {
				'search_text' : $('#search').val(),
				'csrfmiddlewaretoken': $("input[name=csrfmiddlewaretoken]").cal()

			},
			success: searchSuccess,
			dataType: 'html'
		});
	});
});

function searchSuccess(data, textStatus, jqXHR)
{
	$('#search-results').html(data);
}
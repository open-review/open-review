# TODO: Move to static/js (?)
$('.listing li').click -> window.location.href = $(this).find('a:first').attr('href')

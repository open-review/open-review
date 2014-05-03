class ReviewBox
  ADD_COMMENT_HTML = '<a href="#" class="add-comment">Add comment?</a>'

  constructor: (@$elem) ->
    @$lastParagraph = @$elem.find('article.content p:last')

  appendAddCommentPrompt: (onClick) ->
    $(ADD_COMMENT_HTML).appendTo(@$lastParagraph).on('click', -> onClick(); false)

class CommentsBox
  constructor: (@$elem) ->

  count: -> @$elem.find('.comment').length

  hasComments: -> @count() > 0

  isEmpty: -> !@hasComments()

  hide: -> @$elem.hide(); @;

  show: -> @$elem.show(); @;

  focusInput: -> @$elem.find('input').focus(); @;

$('.review.box').each ->
  reviewBox = new ReviewBox($(this));
  commentsBox = new CommentsBox($(this).next('.comments.box'))

  if commentsBox.isEmpty()
    reviewBox.appendAddCommentPrompt -> commentsBox.show().focusInput()
    commentsBox.hide()

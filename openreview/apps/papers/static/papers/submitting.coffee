window.location.extractHash = -> window.location.hash.substring(1)

class PaperDetailsBox
  constructor: (@$elem, @$submissionType) ->
    @$submissionType.change (evt) => @setSubmissionType($(evt.target).val())
    $(window).on('load', $.proxy(@setSubmissionType, @, window.location.extractHash()))

  hasSubmissionType: (type) ->
    $('#' + type + '-details').length > 0

  getSubmissionType: ->
    @$submissionType.val()

  setSubmissionType: (type) ->
    return unless (@hasSubmissionType(type) || @getSubmissionType() == type)
    @$elem.children('form').hide()
    $('#' + type + '-details').show()
    window.location.hash = '#' + type
    @$submissionType.val(type)

class PaperDetailsFetcher
  constructor: (@$form) ->
    @$fetcherResults = @$form.find('.fetcher-results')
    @$identifier = @$form.find('input[type=text]:first')
    @$identifier.keyup($.debounce((=> @reloadDetails()), 150))

  buildURL: (identifier) ->
    "/papers/#{@$form.attr('id').split('-')[0]}/#{identifier}"

  executeRequest: (onSuccess, onFailure) ->
    $.get @buildURL(@$identifier.val()), (data) =>
      if data.error then onFailure(data.error) else onSuccess(data)

  reloadDetails: ->
    @showLoadingIndicator()
    @executeRequest($.proxy(@showDetails, @), $.proxy(@showFailureMessage, @))

  showLoadingIndicator: ->
    @$fetcherResults.removeClass('error success').addClass('loading').text('Loading')

  showFailureMessage: (message) ->
    @$fetcherResults.addClass('error').removeClass('success loading').show().text(
      "#{message}: #{@$identifier.val()}"
    )

  showDetails: (details) ->
    @$fetcherResults.addClass('success').removeClass('error loading').show().html("
      <a href=\"#{details.urls}\">#{details.title}</a>
    ")


new PaperDetailsBox($('.box.paper-details'), $('#submission-type'))
$('.box.paper-details form').each -> new PaperDetailsFetcher($(this))

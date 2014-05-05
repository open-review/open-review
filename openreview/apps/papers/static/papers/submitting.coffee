window.location.extractHash = -> window.location.hash.substring(1)

class PaperDetailsBox
  constructor: (@$elem, @$submissionTypeSelect) ->
    @$submissionTypeSelect.change -> paperDetailsBox.switchSubmissionType($(this).val())

  hasSubmissionType: (type) ->
    $('#' + type + '-details').length > 0

  switchSubmissionType: (type) ->
    return unless @hasSubmissionType(type)
    @$elem.children('form').hide()
    $('#' + type + '-details').show()
    window.location.hash = '#' + type
    @$submissionTypeSelect.val(type)

paperDetailsBox = new PaperDetailsBox($('.box.paper-details'), $('#submission-type'))

$(window).on 'hashchange load', -> paperDetailsBox.switchSubmissionType(window.location.extractHash())

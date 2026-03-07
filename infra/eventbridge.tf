# EventBridge rule: run Lambda on schedule (e.g. daily 6 AM IST)
resource "aws_cloudwatch_event_rule" "calendar_check" {
  name                = "${var.project_name}-daily-calendar-check"
  description         = "Trigger event detector Lambda for calendar alerts"
  schedule_expression = var.calendar_schedule_cron
}

resource "aws_cloudwatch_event_target" "calendar_check_lambda" {
  rule      = aws_cloudwatch_event_rule.calendar_check.name
  target_id = "EventDetectorLambda"
  arn       = aws_lambda_function.event_detector.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.event_detector.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.calendar_check.arn
}

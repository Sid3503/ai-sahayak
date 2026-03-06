data "archive_file" "event_detector" {
  type        = "zip"
  source_file = "${path.module}/lambda/event_detector.py"
  output_path = "${path.module}/build/event_detector.zip"
}

resource "aws_iam_role" "event_detector" {
  name = "${var.project_name}-event-detector-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = { Service = "lambda.amazonaws.com" }
      }
    ]
  })
}

resource "aws_iam_role_policy" "event_detector" {
  name = "${var.project_name}-event-detector-policy"
  role = aws_iam_role.event_detector.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject"]
        Resource = "${aws_s3_object.calendar.arn}"
      },
      {
        Effect   = "Allow"
        Action   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

resource "aws_lambda_function" "event_detector" {
  filename         = data.archive_file.event_detector.output_path
  function_name    = "${var.project_name}-event-detector"
  role             = aws_iam_role.event_detector.arn
  handler          = "event_detector.handler"
  source_code_hash = data.archive_file.event_detector.output_base64sha256
  runtime          = "python3.12"
  timeout          = 30

  environment {
    variables = {
      CALENDAR_BUCKET      = aws_s3_bucket.calendar.id
      CALENDAR_KEY         = aws_s3_object.calendar.key
      BACKEND_WEBHOOK_URL  = var.backend_webhook_url
    }
  }
}

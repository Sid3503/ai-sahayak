resource "aws_s3_bucket" "calendar" {
  bucket = "${var.project_name}-calendar-${data.aws_caller_identity.current.account_id}"

  tags = {
    Project = var.project_name
  }
}

resource "aws_s3_bucket_versioning" "calendar" {
  bucket = aws_s3_bucket.calendar.id

  versioning_configuration {
    status = "Disabled"
  }
}

# Sample calendar (Digital Panchang style); replace with your own events
locals {
  calendar_json = jsonencode({
    events = [
      {
        id                 = "holi-2025"
        name               = "Holi"
        type               = "festival"
        date               = "2025-03-14"
        regions            = ["IN"]
        days_advance_alert = [30, 14, 7, 3, 1]
      },
      {
        id                 = "diwali-2025"
        name               = "Diwali"
        type               = "festival"
        date               = "2025-10-20"
        regions            = ["IN"]
        days_advance_alert = [30, 14, 7, 3, 1]
      }
    ]
  })
}

resource "aws_s3_object" "calendar" {
  bucket  = aws_s3_bucket.calendar.id
  key     = "panchang/events.json"
  content = local.calendar_json
  etag    = md5(local.calendar_json)
}

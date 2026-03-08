# Demo script: get alerts during the video (right now)

Use this so alerts actually fire while you record.

---

## Option A — Trigger alerts right now (no waiting)

Lambda supports **test mode**: it sends alerts to all 5 users **ignoring their alert time**, so you get alerts immediately when you invoke it.

### 1. In AWS Console

1. Open **Lambda** → your **alerts / event-detector** function (the one that reads DynamoDB users + S3 panchang and POSTs to backend webhook).
2. Open the **Test** tab.
3. Create a new test event, name it e.g. **DemoNow**.
4. Event JSON:
   ```json
   {"test_ignore_time": true}
   ```
5. Click **Test**. Lambda runs and POSTs festival alerts for all 5 users (raju, ramesh, suresh, kanta, lakshmi) to your backend.
6. In your app: open **My day** or **Live Alerts**, select **Raju** (or any user) — you should see the new alerts within a few seconds.

### 2. From AWS CLI (Cloud Shell or laptop)

Replace `YOUR_ALERT_LAMBDA_NAME` with the actual function name (e.g. `ai-sahayak-daily-calendar-check` or whatever you see in Lambda console):

```bash
aws lambda invoke \
  --function-name YOUR_ALERT_LAMBDA_NAME \
  --payload '{"test_ignore_time": true}' \
  --cli-binary-format raw-in-base64-out \
  response.json
cat response.json
```

Then open Dashboard → My day → pick a user and show the new alerts.

---

## Option B — Use real schedule (alert at a set time)

If you want to say “every day at 2 PM they get the alert” and then show it at 2 PM:

1. **DynamoDB**  
   For all 5 users in `ai-sahayak-users`, set:
   - `alert_time_hour_ist` = **14**
   - `alert_time_minute_ist` = **0**

2. **EventBridge**  
   Ensure the rule that triggers the Lambda runs at least at **14:00 IST** (e.g. `cron(30 8 * * ? *)` for 14:00 IST if the rule is in UTC).

3. **Record**  
   Start recording before 2 PM IST; when the clock hits 2 PM, Lambda runs and alerts appear in My day.

---

## Suggested flow for the video (Option A)

1. **Intro**  
   “We have 5 kirana owners: Raju and Ramesh in MP, Suresh in Rajasthan, Kanta in Gujarat, Lakshmi in Telangana. Each gets proactive alerts based on their state’s calendar.”

2. **Show setup (optional)**  
   Quick shot: DynamoDB table with the 5 users and their cities/states; S3 `panchang/` with national + regional JSONs.

3. **Trigger alerts**  
   “To show it live, we trigger the alert engine now.”  
   Run Lambda Test with `{"test_ignore_time": true}` (or the CLI command above).

4. **Show result**  
   Open Dashboard → **My day** → select **Raju**.  
   “Raju gets his daily alert — festival reminders and stock hints for Indore, MP.”  
   Switch to **Suresh** / **Kanta** / **Lakshmi** and show their alerts too.

5. **Wrap**  
   “Same flow runs daily on schedule; we just triggered it now for the demo.”

---

## Checklist before recording

- [ ] Backend (agents API) is running and reachable from Lambda (BACKEND_WEBHOOK_URL correct in Lambda env).
- [ ] DynamoDB has all 5 users (raju, ramesh, suresh, kanta, lakshmi) with `city`, `state`.
- [ ] S3 `panchang/` has `national.json` + `regional_mp.json`, `regional_rj.json`, `regional_gj.json`, `regional_ap_ts.json`.
- [ ] You know the Lambda function name for the alerts (for CLI) or have the Test event ready in console.

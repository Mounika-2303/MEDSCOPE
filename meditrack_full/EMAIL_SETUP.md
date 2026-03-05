# Email setup for pharmacy alerts

Alerts are sent to pharmacy emails when medicines are **expired** or **expiring within 30 days**.

## 1. Create `.env`

Copy `.env.example` to `.env` in the project root:

```bash
copy .env.example .env
```

Edit `.env` and set:

- `GMAIL_SENDER` – your Gmail address (e.g. `you@gmail.com`)
- `GMAIL_APP_PASSWORD` – your Gmail **App Password** (see below)
- `ADMIN_EMAIL` – optional; CC’d on alert emails

## 2. Gmail App Password

1. Turn on **2-Step Verification** for your Google account:  
   [Google Account → Security → 2-Step Verification](https://myaccount.google.com/security)
2. Create an **App Password**:  
   [Google Account → Security → App passwords](https://myaccount.google.com/apppasswords)  
   - Choose “Mail” and your device, then generate.
3. Copy the 16-character password (e.g. `abcd efgh ijkl mnop`) into `.env` as:
   ```env
   GMAIL_APP_PASSWORD=abcdefghijklmnop
   ```
   You can paste it with or without spaces; the app removes spaces automatically.

**Important:** Use an **App Password**, not your normal Gmail password.

## 3. Test alerts

1. Log in as **Admin**.
2. On the Admin Dashboard, click **“Send expiry alerts now”**.
3. Check the pharmacy inbox (and ADMIN_EMAIL if set). Check the console for `📧 Email sent to ...` or any error message.

If it fails, the console will show whether SMTP (port 465 or 587) failed; fix Gmail settings or firewall if needed.

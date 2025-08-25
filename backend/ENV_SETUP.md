# Environment Setup Guide

## Email Configuration (REQUIRED for password reset to work)

To make the password reset functionality work, you need to set up email credentials. Here are the steps:

### Option 1: Gmail Setup (Recommended)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate an App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail"
   - Copy the 16-character password

3. **Set Environment Variables**:
   ```bash
   # Windows (PowerShell)
   $env:EMAIL_USER="your-email@gmail.com"
   $env:EMAIL_PASSWORD="your-16-char-app-password"
   $env:EMAIL_HOST="smtp.gmail.com"
   $env:EMAIL_PORT="587"

   # Windows (Command Prompt)
   set EMAIL_USER=your-email@gmail.com
   set EMAIL_PASSWORD=your-16-char-app-password
   set EMAIL_HOST=smtp.gmail.com
   set EMAIL_PORT=587

   # Linux/Mac
   export EMAIL_USER="your-email@gmail.com"
   export EMAIL_PASSWORD="your-16-char-app-password"
   export EMAIL_HOST="smtp.gmail.com"
   export EMAIL_PORT="587"
   ```

### Option 2: Other Email Providers

For other providers, adjust these settings:
```bash
# Outlook/Hotmail
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587

# Yahoo
EMAIL_HOST=smtp.mail.yahoo.com
EMAIL_PORT=587

# Custom SMTP
EMAIL_HOST=your-smtp-server.com
EMAIL_PORT=587
```

### Option 3: Test Without Email (Development Only)

If you want to test without setting up email, you can modify the backend to log the reset link instead of sending email. But this is NOT recommended for production.

## Testing the Setup

1. **Set the environment variables** (see above)
2. **Restart your backend server**
3. **Try the forgot password flow**:
   - Go to Sign In page
   - Click "Forgot your password?"
   - Enter a registered email
   - Check your email for the reset link

## Troubleshooting

- **"Failed to send email"**: Check your email credentials and 2FA setup
- **"Copy link" not working**: The reset link format has been fixed
- **No email received**: Check spam folder, verify email credentials
- **Backend errors**: Check console for detailed error messages

## Security Notes

- Never commit real email credentials to version control
- Use environment variables or secure configuration files
- App passwords are more secure than regular passwords
- Consider using a dedicated email service for production

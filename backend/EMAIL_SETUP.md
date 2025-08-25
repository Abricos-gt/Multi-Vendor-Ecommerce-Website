# Email Setup for Password Reset

To enable actual email sending for password reset functionality, you need to configure email settings.

## Option 1: Gmail (Recommended for Development)

### 1. Enable 2-Factor Authentication on your Gmail account

### 2. Generate an App Password
- Go to Google Account settings
- Security → 2-Step Verification → App passwords
- Generate a new app password for "Mail"
- Copy the 16-character password

### 3. Set Environment Variables
Create a `.env` file in the backend directory with:

```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-16-char-app-password
```

## Option 2: Other Email Services

### SendGrid
```bash
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USER=apikey
EMAIL_PASSWORD=your-sendgrid-api-key
```

### Mailgun
```bash
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_USER=your-mailgun-username
EMAIL_PASSWORD=your-mailgun-password
```

## Option 3: Local Development (No Email)

If you want to test without sending emails, you can modify the backend to skip email sending:

```python
# In app.py, comment out the email sending line:
# email_sent = send_password_reset_email(user.email, reset_url, user_name)

# And always return success:
return jsonify({
    'message': 'Password reset link generated (email disabled in development)',
    'reset_url': reset_url,
    'expires_at': expires_at.isoformat()
})
```

## Testing

1. Set up your email configuration
2. Restart the backend server
3. Try the forgot password functionality
4. Check your email for the reset link

## Security Notes

- Never commit your actual email credentials to version control
- Use environment variables for sensitive information
- Consider using email service APIs instead of SMTP for production
- Implement rate limiting for password reset requests

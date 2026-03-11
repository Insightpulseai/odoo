import nodemailer from 'nodemailer'

const transporter = nodemailer.createTransport({
  host: 'smtp.zoho.com',
  port: 587,
  secure: false, // TLS
  auth: {
    user: process.env.ZOHO_USER!,
    pass: process.env.ZOHO_PASS!,
  },
})

export interface OrgInviteEmailData {
  to: string
  orgName: string
  role: string
  token: string
  inviterName: string
  expiresAt: Date
}

export async function sendOrgInviteEmail(data: OrgInviteEmailData) {
  const acceptUrl = `${process.env.NEXT_PUBLIC_APP_URL}/invite/accept?token=${data.token}`

  await transporter.sendMail({
    from: `"${process.env.ZOHO_FROM_NAME}" <${process.env.ZOHO_USER}>`,
    to: data.to,
    subject: `Invitation to join ${data.orgName}`,
    html: `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
      </head>
      <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
          <h1 style="color: white; margin: 0; font-size: 28px;">You've Been Invited!</h1>
        </div>

        <div style="background: #ffffff; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
          <p style="font-size: 16px; margin-bottom: 20px;">
            <strong>${data.inviterName}</strong> has invited you to join <strong>${data.orgName}</strong> as a <strong>${data.role}</strong>.
          </p>

          <div style="text-align: center; margin: 30px 0;">
            <a href="${acceptUrl}" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block; font-size: 16px;">
              Accept Invitation
            </a>
          </div>

          <p style="color: #666; font-size: 14px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
            This invitation expires on <strong>${data.expiresAt.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</strong>.
          </p>

          <p style="color: #999; font-size: 12px; margin-top: 20px;">
            If the button doesn't work, copy and paste this link into your browser:<br>
            <a href="${acceptUrl}" style="color: #667eea; word-break: break-all;">${acceptUrl}</a>
          </p>
        </div>
      </body>
      </html>
    `,
    text: `
You've been invited!

${data.inviterName} has invited you to join ${data.orgName} as a ${data.role}.

Accept your invitation by visiting: ${acceptUrl}

This invitation expires on ${data.expiresAt.toLocaleDateString()}.

If you have trouble clicking the link, copy and paste this URL into your browser:
${acceptUrl}
    `.trim()
  })
}

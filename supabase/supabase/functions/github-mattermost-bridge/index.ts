// Supabase Edge Function: GitHub to Mattermost Bridge
// Routes GitHub events to Mattermost channels (like GitHub + Slack integration)

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type, x-hub-signature-256, x-github-event, x-github-delivery',
}

// Mattermost configuration
const MATTERMOST_WEBHOOK_URL = Deno.env.get('MATTERMOST_WEBHOOK_URL')!
const MATTERMOST_BOT_USERNAME = 'GitHub'
const MATTERMOST_BOT_ICON = 'https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png'

// Channel routing
const CHANNEL_ROUTING: Record<string, string> = {
  'push': 'dev-commits',
  'pull_request': 'dev-prs',
  'pull_request_review': 'dev-prs',
  'issues': 'dev-issues',
  'issue_comment': 'dev-issues',
  'release': 'releases',
  'workflow_run': 'ci-cd',
  'check_run': 'ci-cd',
  'deployment': 'deployments',
  'deployment_status': 'deployments',
  'default': 'github-activity'
}

interface GitHubPayload {
  action?: string
  sender?: { login: string; avatar_url: string; html_url: string }
  repository?: { full_name: string; html_url: string; private: boolean }
  organization?: { login: string }
  installation?: { id: number }
  // Event-specific fields
  ref?: string
  commits?: Array<{ message: string; author: { name: string }; url: string; id: string }>
  compare?: string
  pusher?: { name: string }
  pull_request?: {
    number: number
    title: string
    html_url: string
    state: string
    user: { login: string }
    merged: boolean
    draft: boolean
    body?: string
  }
  issue?: {
    number: number
    title: string
    html_url: string
    state: string
    user: { login: string }
    body?: string
  }
  comment?: {
    body: string
    html_url: string
    user: { login: string }
  }
  release?: {
    name: string
    tag_name: string
    html_url: string
    body?: string
    prerelease: boolean
  }
  workflow_run?: {
    name: string
    conclusion: string
    html_url: string
    head_branch: string
  }
  check_run?: {
    name: string
    conclusion: string
    html_url: string
    check_suite: { head_branch: string }
  }
  deployment?: {
    environment: string
    description: string
  }
  deployment_status?: {
    state: string
    environment: string
    description: string
  }
}

serve(async (req: Request) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  if (req.method !== 'POST') {
    return new Response('Method not allowed', { status: 405 })
  }

  const event = req.headers.get('x-github-event')
  const delivery = req.headers.get('x-github-delivery')

  if (!event) {
    return new Response('Missing x-github-event header', { status: 400 })
  }

  try {
    const payload: GitHubPayload = await req.json()

    // Format message based on event type
    const message = formatMessage(event, payload)

    if (!message) {
      // Event not supported, acknowledge but don't post
      return new Response(JSON.stringify({ success: true, action: 'ignored' }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // Determine channel
    const channel = CHANNEL_ROUTING[event] || CHANNEL_ROUTING.default

    // Send to Mattermost
    await sendToMattermost({
      channel,
      ...message
    })

    // Log to Supabase
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    const supabase = createClient(supabaseUrl, supabaseKey)

    await supabase.from('github_mattermost_messages').insert({
      delivery_id: delivery,
      event_type: event,
      action: payload.action,
      repository: payload.repository?.full_name,
      sender: payload.sender?.login,
      channel: channel,
      message_text: message.text?.substring(0, 500),
      sent_at: new Date().toISOString()
    })

    return new Response(JSON.stringify({ success: true, channel, event }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })

  } catch (error) {
    console.error('GitHub-Mattermost bridge error:', error)
    return new Response(JSON.stringify({ success: false, error: error.message }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
})

function formatMessage(event: string, payload: GitHubPayload): MattermostMessage | null {
  const repo = payload.repository?.full_name || 'Unknown repo'
  const repoUrl = payload.repository?.html_url
  const sender = payload.sender?.login || 'Unknown'
  const senderUrl = payload.sender?.html_url

  switch (event) {
    case 'push':
      return formatPushEvent(payload, repo, repoUrl, sender)

    case 'pull_request':
      return formatPullRequestEvent(payload, repo, repoUrl, sender)

    case 'pull_request_review':
      return formatPRReviewEvent(payload, repo, sender)

    case 'issues':
      return formatIssueEvent(payload, repo, repoUrl, sender)

    case 'issue_comment':
      return formatCommentEvent(payload, repo, sender)

    case 'release':
      return formatReleaseEvent(payload, repo, repoUrl)

    case 'workflow_run':
      return formatWorkflowRunEvent(payload, repo, repoUrl)

    case 'check_run':
      return formatCheckRunEvent(payload, repo)

    case 'deployment':
    case 'deployment_status':
      return formatDeploymentEvent(event, payload, repo)

    case 'star':
      if (payload.action === 'created') {
        return {
          text: `⭐ **${sender}** starred [${repo}](${repoUrl})`,
          icon_emoji: ':star:'
        }
      }
      return null

    case 'fork':
      return {
        text: `🍴 **${sender}** forked [${repo}](${repoUrl})`,
        icon_emoji: ':fork_and_knife:'
      }

    default:
      return null
  }
}

function formatPushEvent(payload: GitHubPayload, repo: string, repoUrl: string | undefined, sender: string): MattermostMessage {
  const branch = payload.ref?.replace('refs/heads/', '') || 'unknown'
  const commits = payload.commits || []
  const commitCount = commits.length

  let text = `📤 **${sender}** pushed ${commitCount} commit${commitCount !== 1 ? 's' : ''} to \`${branch}\` in [${repo}](${repoUrl})\n`

  if (payload.compare) {
    text += `[View changes](${payload.compare})\n`
  }

  // Show up to 5 commits
  const displayCommits = commits.slice(0, 5)
  if (displayCommits.length > 0) {
    text += '\n'
    displayCommits.forEach((commit) => {
      const shortSha = commit.id.substring(0, 7)
      const shortMessage = commit.message.split('\n')[0].substring(0, 80)
      text += `• [\`${shortSha}\`](${commit.url}) ${shortMessage}\n`
    })
  }

  if (commits.length > 5) {
    text += `\n_...and ${commits.length - 5} more commits_`
  }

  return {
    text,
    icon_emoji: ':arrow_up:'
  }
}

function formatPullRequestEvent(payload: GitHubPayload, repo: string, repoUrl: string | undefined, sender: string): MattermostMessage {
  const pr = payload.pull_request!
  const action = payload.action
  const prNumber = pr.number
  const prTitle = pr.title
  const prUrl = pr.html_url

  const actionEmoji: Record<string, string> = {
    'opened': '🆕',
    'closed': pr.merged ? '🎉' : '❌',
    'reopened': '🔄',
    'ready_for_review': '👀',
    'converted_to_draft': '📝'
  }

  const emoji = actionEmoji[action || ''] || '📋'
  const actionText = pr.merged ? 'merged' : action

  let text = `${emoji} **${sender}** ${actionText} PR [#${prNumber}](${prUrl}): **${prTitle}** in [${repo}](${repoUrl})`

  if (action === 'opened' && pr.body) {
    const shortBody = pr.body.substring(0, 200)
    text += `\n\n> ${shortBody}${pr.body.length > 200 ? '...' : ''}`
  }

  return {
    text,
    icon_emoji: ':git:'
  }
}

function formatPRReviewEvent(payload: GitHubPayload, repo: string, sender: string): MattermostMessage | null {
  const action = payload.action
  const pr = payload.pull_request!

  if (action !== 'submitted') return null

  return {
    text: `💬 **${sender}** reviewed PR [#${pr.number}](${pr.html_url}): **${pr.title}** in ${repo}`,
    icon_emoji: ':mag:'
  }
}

function formatIssueEvent(payload: GitHubPayload, repo: string, repoUrl: string | undefined, sender: string): MattermostMessage {
  const issue = payload.issue!
  const action = payload.action

  const actionEmoji: Record<string, string> = {
    'opened': '🆕',
    'closed': '✅',
    'reopened': '🔄',
    'assigned': '👤',
    'labeled': '🏷️'
  }

  const emoji = actionEmoji[action || ''] || '📋'

  let text = `${emoji} **${sender}** ${action} issue [#${issue.number}](${issue.html_url}): **${issue.title}** in [${repo}](${repoUrl})`

  if (action === 'opened' && issue.body) {
    const shortBody = issue.body.substring(0, 200)
    text += `\n\n> ${shortBody}${issue.body.length > 200 ? '...' : ''}`
  }

  return {
    text,
    icon_emoji: ':bug:'
  }
}

function formatCommentEvent(payload: GitHubPayload, repo: string, sender: string): MattermostMessage {
  const comment = payload.comment!
  const issue = payload.issue!

  const shortComment = comment.body.substring(0, 200)

  return {
    text: `💬 **${sender}** [commented](${comment.html_url}) on issue [#${issue.number}](${issue.html_url}): **${issue.title}** in ${repo}\n\n> ${shortComment}${comment.body.length > 200 ? '...' : ''}`,
    icon_emoji: ':speech_balloon:'
  }
}

function formatReleaseEvent(payload: GitHubPayload, repo: string, repoUrl: string | undefined): MattermostMessage | null {
  if (payload.action !== 'published') return null

  const release = payload.release!
  const emoji = release.prerelease ? '🧪' : '🚀'

  let text = `${emoji} **New ${release.prerelease ? 'pre-release' : 'release'}** [${release.tag_name}](${release.html_url}) in [${repo}](${repoUrl})`

  if (release.name && release.name !== release.tag_name) {
    text += `\n**${release.name}**`
  }

  if (release.body) {
    const shortBody = release.body.substring(0, 300)
    text += `\n\n${shortBody}${release.body.length > 300 ? '...' : ''}`
  }

  return {
    text,
    icon_emoji: ':rocket:'
  }
}

function formatWorkflowRunEvent(payload: GitHubPayload, repo: string, repoUrl: string | undefined): MattermostMessage | null {
  if (payload.action !== 'completed') return null

  const run = payload.workflow_run!
  const conclusion = run.conclusion

  const statusEmoji: Record<string, string> = {
    'success': '✅',
    'failure': '❌',
    'cancelled': '⏹️',
    'skipped': '⏭️',
    'timed_out': '⏱️'
  }

  const emoji = statusEmoji[conclusion] || '❓'

  return {
    text: `${emoji} Workflow **${run.name}** ${conclusion} on \`${run.head_branch}\` in [${repo}](${repoUrl})\n[View run](${run.html_url})`,
    icon_emoji: ':gear:'
  }
}

function formatCheckRunEvent(payload: GitHubPayload, repo: string): MattermostMessage | null {
  if (payload.action !== 'completed') return null

  const check = payload.check_run!
  const conclusion = check.conclusion

  if (conclusion === 'success') return null // Don't spam on success

  const emoji = conclusion === 'failure' ? '❌' : '⚠️'

  return {
    text: `${emoji} Check **${check.name}** ${conclusion} on \`${check.check_suite.head_branch}\` in ${repo}\n[View check](${check.html_url})`,
    icon_emoji: ':warning:'
  }
}

function formatDeploymentEvent(event: string, payload: GitHubPayload, repo: string): MattermostMessage {
  if (event === 'deployment') {
    const deploy = payload.deployment!
    return {
      text: `🚀 Deployment started to **${deploy.environment}** in ${repo}\n${deploy.description || ''}`,
      icon_emoji: ':rocket:'
    }
  }

  const status = payload.deployment_status!
  const stateEmoji: Record<string, string> = {
    'success': '✅',
    'failure': '❌',
    'error': '❌',
    'pending': '⏳',
    'in_progress': '🔄'
  }

  const emoji = stateEmoji[status.state] || '❓'

  return {
    text: `${emoji} Deployment to **${status.environment}** ${status.state} in ${repo}\n${status.description || ''}`,
    icon_emoji: ':package:'
  }
}

interface MattermostMessage {
  text: string
  icon_emoji?: string
  channel?: string
  attachments?: Array<{
    color?: string
    title?: string
    text?: string
    fields?: Array<{ title: string; value: string; short?: boolean }>
  }>
}

async function sendToMattermost(message: MattermostMessage & { channel: string }) {
  const response = await fetch(MATTERMOST_WEBHOOK_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      channel: message.channel,
      username: MATTERMOST_BOT_USERNAME,
      icon_url: MATTERMOST_BOT_ICON,
      text: message.text,
      props: {
        from_webhook: 'true',
        override_username: MATTERMOST_BOT_USERNAME,
        override_icon_url: MATTERMOST_BOT_ICON
      }
    })
  })

  if (!response.ok) {
    throw new Error(`Mattermost webhook failed: ${response.status}`)
  }
}

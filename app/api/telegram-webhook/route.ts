import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  try {
    const payload = await req.json();

    // Verify if it's a message from a user
    if (!payload.message || !payload.message.text) {
      return NextResponse.json({ status: 'ignored', reason: 'No text message' }, { status: 200 });
    }

    const chatId = String(payload.message.chat.id);
    const text = payload.message.text.trim();

    // Environment keys
    const ALLOWED_CHAT_ID = process.env.ALLOWED_CHAT_ID;
    const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
    const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
    const GITHUB_REPO_OWNER = process.env.GITHUB_REPO_OWNER;
    const GITHUB_REPO_NAME = process.env.GITHUB_REPO_NAME;

    // 1. Authorization: Only process messages from the granted CHAT_ID
    if (chatId !== ALLOWED_CHAT_ID) {
      console.warn(`[Webhook] Intento de acceso no autorizado desde el Chat ID: ${chatId}`);
      // Return 200 to Telegram so it doesn't retry
      return NextResponse.json({ status: 'rejected' }, { status: 200 });
    }

    // 2. Command Evaluation
    if (text === '/scrape') {
      
      // We must notify the user immediately on Telegram
      const tele_url = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`;
      await fetch(tele_url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: chatId,
          text: '🚀 Iniciando búsqueda de oportunidades 2027 en Varsovia... Te avisaré al terminar'
        })
      });

      // 3. Trigger GitHub Actions via repository_dispatch
      const gh_url = `https://api.github.com/repos/${GITHUB_REPO_OWNER}/${GITHUB_REPO_NAME}/dispatches`;
      
      const gh_response = await fetch(gh_url, {
        method: 'POST',
        headers: {
          'Accept': 'application/vnd.github.v3+json',
          'Authorization': `Bearer ${GITHUB_TOKEN}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          event_type: 'manual_trigger'
        })
      });

      if (!gh_response.ok) {
        console.error("[Webhook] GitHub Action deployment failed:", await gh_response.text());
        return NextResponse.json({ status: 'github_error' }, { status: 500 });
      }

      return NextResponse.json({ status: 'triggered' }, { status: 200 });
    }

    // If it's a command we don't recognize
    return NextResponse.json({ status: 'ignored_command' }, { status: 200 });

  } catch (error) {
    console.error('[Webhook] Internal error:', error);
    return NextResponse.json({ error: 'Internal error' }, { status: 500 });
  }
}

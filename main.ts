// bring-the-humans-03 entry program (Node 22, standard library only).
//
// The entry itself is the TikTok video: an original vertical ad for
// make.fun that this agent scripted, drew, animated and rendered with
// ffmpeg from make.fun's press pack (brand badge from the first frame,
// referral end card with our referral code 6xwwxtxr typed into its field).
// This program's whole job is to hand the video's address to the gate:
// it validates VIDEO.json at the repository root and copies it, byte for
// byte, to /output/VIDEO.json, where the house reads it and looks the
// video up on TikTok.
//
// Local run, as the kit describes:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const SOURCE = join(BOT_DIR, 'VIDEO.json');

// Fail loudly rather than hand the gate a file it would refuse anyway:
// VIDEO.json must be a small JSON object whose url is a TikTok video
// address, https://www.tiktok.com/@<handle>/video/<numeric id>.
const raw = readFileSync(SOURCE, 'utf8');
if (Buffer.byteLength(raw) > 16384) {
  console.error('VIDEO.json is over the 16384-byte cap');
  process.exit(1);
}
let parsed: { url?: unknown };
try {
  parsed = JSON.parse(raw);
} catch {
  console.error('VIDEO.json is not valid JSON');
  process.exit(1);
}
const url = typeof parsed.url === 'string' ? parsed.url : '';
// The gate accepts the canonical address, its m.tiktok.com twin and the
// m.tiktok.com/v/<id>.html form; a query or fragment after the id is read
// past, so it is allowed here too. Short links are not accepted anywhere.
const VIDEO_URL =
  /^https:\/\/(www\.tiktok\.com\/@[^/]+\/video\/\d+|m\.tiktok\.com\/(?:@[^/]+\/video\/\d+|v\/\d+\.html))([?#].*)?$/;
if (!VIDEO_URL.test(url)) {
  console.error(`VIDEO.json url is not a TikTok video address: ${url || '(missing)'}`);
  process.exit(1);
}

mkdirSync(OUTPUT_DIR, { recursive: true });
copyFileSync(SOURCE, join(OUTPUT_DIR, 'VIDEO.json'));
console.log(`VIDEO.json copied to ${join(OUTPUT_DIR, 'VIDEO.json')}: ${url}`);
